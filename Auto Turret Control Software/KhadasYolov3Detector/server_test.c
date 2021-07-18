#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <stdio.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <errno.h>

int main() {
  int i, counter, max_clients, client_socket[1], master_listen_socket, flags;

  counter = 0;

  for (i = 0; i < max_clients; i++)  
    {  
        client_socket[i] = 0;  
    }

  if ((master_listen_socket = socket(AF_INET, SOCK_STREAM, 0)) < 0)
  {
      perror("Socket create failure"); 
      exit(EXIT_FAILURE);
  }
  
  if ((flags = fcntl(master_listen_socket, F_GETFL)) < 0)
  {
      perror("Failed to get flags"); 
      exit(EXIT_FAILURE);
  }

  if (fcntl(master_listen_socket, F_SETFL, flags | O_NONBLOCK) < 0)
  {
      perror("Failed to set socket to non-blocking"); 
      exit(EXIT_FAILURE);
  }
  
  struct sockaddr_in addr;
  addr.sin_family = AF_INET;
  addr.sin_port = htons(4141);
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  
  if(bind(master_listen_socket, (struct sockaddr *) &addr, sizeof(addr)) < 0)
  {
      perror("Failed to bind to socket on 4141"); 
      exit(EXIT_FAILURE);
  }
  
  if (listen(master_listen_socket, 100) < 0)
  {
      perror("Can't listen on socket"); 
      exit(EXIT_FAILURE);
  }
  
  while (1)
  {
    int client_socket_fd = accept(master_listen_socket, NULL, NULL);
    if (client_socket_fd == -1) 
    {
      if (errno == EWOULDBLOCK)
      {
        printf("No pending connections\n");
        if (client_socket[0] != 0)
        {       
            printf("Sending next message...");
            int length = snprintf( NULL, 0, "Next message: %d", counter );
            char* msg = (char*)malloc( length + 5 );
            snprintf( msg, length + 5, "Next message: %d", counter );
            //char msg[] = printf("next message: %s\n", counter);
            send(client_socket[0], msg, strlen(msg), 0);
            free(msg);
            counter++;
        }
        sleep(1);
      }
      else
      {
        perror("Failed to accept connection");
        exit(EXIT_FAILURE);
      }
    }
    else
    {
      char msg[] = "hello\n";
      printf("Got a connection; writing 'hello'.\n");
      send(client_socket_fd, msg, sizeof(msg), 0);
      client_socket[0] = client_socket_fd;
      //close(client_socket_fd);
    }
  }
  return EXIT_SUCCESS;
}