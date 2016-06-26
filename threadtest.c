#include "types.h"
#include "user.h"

unsigned short lfsr = 0xACE1u;
unsigned bit;

//generate a random number
unsigned rand()
{
	bit = ((lfsr >> 0) ^ (lfsr >> 2) ^ (lfsr >> 3) ^ (lfsr >> 5)) & 1;
	return lfsr = (lfsr >> 1) | (bit << 15);
}

//Show an error message and then exit.
void error(char* message)
{
	printf(1, "Error: %s\n", message);
	exit();
}

//A finite buffer to store data for Producer/Consumer
#define BufSize 10
struct Buffer
{
	int data[BufSize];
	int current;
};

struct Buffer buffer;

//put a value into buffer
void bufferAdd(int value)
{
	if (buffer.current >= BufSize) error("Buffer full.");
	buffer.data[++buffer.current] = value;
}

//get a value from buffer
int bufferGet()
{
	if (buffer.current < 0) error("Buffer empty.");
	return buffer.data[buffer.current--];
}

//Producer thread
void producer(void * arg)
{
	int iteration = *(int *)arg;
	int count;
	for (count = 0; count < iteration; count++) {

		//produce something after taking a random time
		int i, j, garbage;
		for (i = 0; i < 10; i++) {
			int rand_num = rand() * 200;
			for (j = 0; j < rand_num; j++) {
				garbage += 1;
			}
		}

		//add produce to buffer
		printf(1, "Producer generated an item %d\n", count);
		bufferAdd(count);
		printf(1, "Producer added item %d to buffer\n", count);
	}
}

//Consumer thread
void consumer(void * arg)
{
	int iteration = *(int *)arg;
	int count;
	for (count = 0; count < iteration; count++) {

		//get an item from buffer
		printf(1, "Consumer want to get next item from buffer\n");
		int data = bufferGet(count);
		printf(1, "Consumer got an item %d from buffer\n", data);

		//process the item after taking a random time
		int i, j, garbage;
		for (i = 0; i < 10; i++) {
			int rand_num = rand() * 200;
			for (j = 0; j < rand_num; j++) {
				garbage += 1;
			}
		}
	}
}

int main(int argc, char *argv[])
{
	printf(1, "*** Machine Problem 2: Kernel Thread Test ***\n");
	buffer.current = -1;

	//prepare thread argument
	int iteration = 50;
	int *arg = &iteration;

	//create producer thread
	uint* stack1 = (uint*)malloc(32 * sizeof(uint));
	int producerId = thread_create(producer, (void*)stack1, (void*)arg);
	printf(1, "Producer thread %d created.\n", producerId);

	//create consumer thread
	uint* stack2 = (uint*)malloc(32 * sizeof(uint));
	int consumerId = thread_create(consumer, (void*)stack2, (void*)arg);
	printf(1, "Consumer thread %d created.\n", consumerId);

	//wait until all child thread are exit
	uint* stack = (uint*)0;
	int threadId;
	while ((threadId = thread_join((void*)stack)) != -1) {
		printf(1, "Thread %d finished.\n", threadId);
		free(stack);
	}

	printf(1, "Main function exiting. Buffer size %d\n", buffer.current);
	exit();
	return 0;
}
