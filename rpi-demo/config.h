#ifndef CONFIG_H_
#define CONFIG_H_

#define PANELSX     9
#define PANELSY     6


// The number of panels on the bus.
#define CONFIG_BUS_LENGTH       (PANELSX * PANELSY)

// Physical dimension (One long string going up)
#define XP  16
#define YP  (20 * CONFIG_BUS_LENGTH)

// Logical dimension (panels in a matrix configuration)
#define XL  (16 * PANELSX)
#define YL  (20 * PANELSY)
#define LEFT_TO_RIGHT   1

#define INVERT_GPIO  0

#endif
