// Reads raw yuv420p frames on stdin, finds tag36h11 tags, and broadcasts each pose as one UDP JSON line.
// Usage: tagstream <width> <height> <fx> <fy> <cx> <cy> <decimate> <port>
// Camera axes: x right, y down, z out of the lens. Older frames are dropped so results stay current.
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <math.h>
#include <net/if.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>
#include "apriltag.h"
#include "apriltag_pose.h"
#include "tag36h11.h"

static int W, H, port, sock;
static uint8_t *latest;
static unsigned long seq_in, seq_done_eof;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
static struct sockaddr_in dest[8];
static int ndest;

static double now_ms(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e3 + t.tv_nsec / 1e6; }

// Printed black-square size in metres; unknown ids use the 5 cm size.
static double tag_size(int id) { return id == 0 ? 0.0298 : id == 2 ? 0.0799 : 0.0501; }

static void refresh_dests(void) {
    struct ifaddrs *a, *i;
    ndest = 0;
    if (getifaddrs(&a)) return;
    for (i = a; i && ndest < 8; i = i->ifa_next) {
        if (!i->ifa_addr || i->ifa_addr->sa_family != AF_INET) continue;
        if (!(i->ifa_flags & IFF_BROADCAST) || !(i->ifa_flags & IFF_UP) || !i->ifa_broadaddr) continue;
        dest[ndest] = *(struct sockaddr_in *)i->ifa_broadaddr;
        dest[ndest].sin_port = htons(port);
        ndest++;
    }
    freeifaddrs(a);
}

static void send_line(const char *s) {
    for (int i = 0; i < ndest; i++) sendto(sock, s, strlen(s), 0, (struct sockaddr *)&dest[i], sizeof dest[i]);
}

static void *reader(void *arg) {
    size_t n = (size_t)W * H * 3 / 2;
    uint8_t *buf = malloc(n);
    for (;;) {
        size_t got = 0;
        while (got < n) {
            ssize_t r = read(0, buf + got, n - got);
            if (r <= 0) { pthread_mutex_lock(&mu); seq_done_eof = 1; pthread_cond_signal(&cv); pthread_mutex_unlock(&mu); return NULL; }
            got += r;
        }
        pthread_mutex_lock(&mu);
        memcpy(latest, buf, (size_t)W * H);
        seq_in++;
        pthread_cond_signal(&cv);
        pthread_mutex_unlock(&mu);
    }
}

int main(int c, char **v) {
    if (c < 9) { fprintf(stderr, "usage: tagstream w h fx fy cx cy decimate port\n"); return 2; }
    W = atoi(v[1]); H = atoi(v[2]);
    double fx = atof(v[3]), fy = atof(v[4]), cx = atof(v[5]), cy = atof(v[6]);
    port = atoi(v[8]);
    latest = malloc((size_t)W * H);
    uint8_t *work = malloc((size_t)W * H);
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    int on = 1;
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &on, sizeof on);
    refresh_dests();

    apriltag_family_t *tf = tag36h11_create();
    apriltag_detector_t *td = apriltag_detector_create();
    apriltag_detector_add_family_bits(td, tf, 1);
    td->quad_decimate = atof(v[7]); td->quad_sigma = 0; td->nthreads = 1; td->refine_edges = 1;

    pthread_t th;
    pthread_create(&th, NULL, reader, NULL);
    unsigned long seen = 0, processed = 0, last_in = 0, msg = 0;
    double last_hb = now_ms(), det_sum = 0;
    int det_n = 0;
    image_u8_t im = {.width = W, .height = H, .stride = W, .buf = work};
    char line[320];
    for (;;) {
        pthread_mutex_lock(&mu);
        while (seq_in == seen && !seq_done_eof) pthread_cond_wait(&cv, &mu);
        if (seq_in == seen && seq_done_eof) { pthread_mutex_unlock(&mu); return 0; }
        seen = seq_in;
        memcpy(work, latest, (size_t)W * H);
        pthread_mutex_unlock(&mu);

        double t0 = now_ms();
        zarray_t *dets = apriltag_detector_detect(td, &im);
        double det_ms = now_ms() - t0;
        for (int i = 0; i < zarray_size(dets); i++) {
            apriltag_detection_t *d;
            zarray_get(dets, i, &d);
            if (d->decision_margin < 25) continue;
            apriltag_detection_info_t info = {d, tag_size(d->id), fx, fy, cx, cy};
            apriltag_pose_t p;
            estimate_tag_pose(&info, &p);
            double *R = p.R->data;
            double px = hypot(d->p[0][0] - d->p[1][0], d->p[0][1] - d->p[1][1]);
            snprintf(line, sizeof line,
                     "{\"seq\":%lu,\"t_ms\":%.0f,\"id\":%d,\"x_cm\":%.2f,\"y_cm\":%.2f,\"z_cm\":%.2f,"
                     "\"roll\":%.1f,\"pitch\":%.1f,\"yaw\":%.1f,\"px\":%.0f,\"margin\":%.0f,\"det_ms\":%.0f}\n",
                     ++msg, now_ms(), d->id, p.t->data[0] * 100, p.t->data[1] * 100, p.t->data[2] * 100,
                     atan2(R[3], R[0]) * 57.2958, atan2(-R[6], hypot(R[7], R[8])) * 57.2958, atan2(R[7], R[8]) * 57.2958,
                     px, d->decision_margin, det_ms);
            send_line(line);
            matd_destroy(p.R); matd_destroy(p.t);
        }
        apriltag_detections_destroy(dets);
        processed++; det_sum += det_ms; det_n++;
        double t = now_ms();
        if (t - last_hb > 1000) {
            snprintf(line, sizeof line, "{\"hb\":1,\"t_ms\":%.0f,\"in_fps\":%.1f,\"det_fps\":%.1f,\"det_ms\":%.0f}\n",
                     t, (seen - last_in) * 1000.0 / (t - last_hb), det_n * 1000.0 / (t - last_hb), det_n ? det_sum / det_n : 0);
            send_line(line);
            last_in = seen; last_hb = t; det_sum = 0; det_n = 0;
            refresh_dests();
        }
    }
}
