/*                     -*- mode: C; c-file-style: "stroustrup"; -*-
 *
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

#include "flipdot_net.h"
#include <stdint.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <strings.h>
#include <stdint.h>

int sockfd;
struct sockaddr_in servaddr;

void
flipdot_net_init (void)
{
    sockfd=socket(AF_INET,SOCK_DGRAM,0);

    bzero(&servaddr,sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr=htonl(INADDR_ANY);
    servaddr.sin_port=htons(2323);
    bind(sockfd,(struct sockaddr *)&servaddr,sizeof(servaddr));
}

int
flipdot_net_recv_frame(uint8_t *buffer, int size)
{
    return recv(sockfd,buffer,size,0);
}

