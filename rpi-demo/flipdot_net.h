/*
 * Copyright (c) 2013 by Tobias Schneider
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by 
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 * For more information on the GPL, please go to:
 * http://www.gnu.org/copyleft/gpl.html
 */

#ifndef FLIPDOT_NET_H
#define FLIPDOT_NET_H

#include <stdint.h>
#if 0
struct flipdot_packet
{
    uint8_t panel_number;
    uint8_t command;
    uint8_t frame[16*20];
}__attribute__((packed));
#endif

void flipdot_net_init(void);
int flipdot_net_recv_frame(uint8_t *buffer, int size);

#endif /* FLIPDOT_NET_H */
