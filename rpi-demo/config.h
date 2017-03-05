#ifndef CONFIG_H_
#define CONFIG_H_

// The number of active buses (A, B, C, D)
#define CONFIG_BUS_COUNT        1

// The number of panels on each bus.
#define CONFIG_BUS_LENGTH       (18 * 3)

#define XP  16
#define YP  (20 * CONFIG_BUS_LENGTH)

#define XL  (16 * 9)
#define YL  (20 * 6)

#endif
