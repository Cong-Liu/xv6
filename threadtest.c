#include "types.h"
#include "user.h"
#include "spinlock.h"

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

int mutexLock;
int itemsLock;
int spacesLock;

//put a value into buffer
void bufferAdd(int value)
{
	//wait for space
	mtx_lock(mutexLock);
	if (buffer.current >= BufSize) mtx_lock(spacesLock);
	mtx_unlock(mutexLock);

	//add item to buffer
	mtx_lock(mutexLock);
	buffer.data[++buffer.current] = value;
	mtx_unlock(mutexLock);

	//notify other thread items are available
	mtx_lock(mutexLock);
	if (buffer.current == 0) mtx_unlock(itemsLock);
	mtx_unlock(mutexLock);	
}

//get a value from buffer
int bufferGet()
{
	//wait for an item
	mtx_lock(mutexLock);
	if (buffer.current < 0) mtx_lock(itemsLock);
	mtx_unlock(mutexLock);
	
	//get item from buffer
	mtx_lock(mutexLock);
	int item = buffer.data[buffer.current--];
	mtx_unlock(mutexLock);

	//notify other thread spaces are available
	mtx_lock(mutexLock);
	if (buffer.current == BufSize - 1) mtx_unlock(spacesLock);
	mtx_unlock(mutexLock);	

	return item;
}

//Producer thread
void producer(void * arg)
{
	int iteration = *(int *)arg;

	printf(1, "Producer started with param %d\n", iteration);
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

	exit();
}

//Consumer thread
void consumer(void * arg)
{
	int iteration = *(int *)arg;

	printf(1, "Consumer started with param %d\n", iteration);
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

	exit();
}

int main(int argc, char *argv[])
{
	printf(1, "*** Machine Problem 2: Kernel Thread Test ***\n");
	buffer.current = -1;

	//initialize 3 locks
	mutexLock = mtx_create(0);
	itemsLock = mtx_create(0);
	spacesLock = mtx_create(0);
	//printf(1, "Lock: Mutex %d, Items %d, Spaces %d\n", mutexLock, itemsLock, spacesLock);

	//prepare thread argument
	int iteration = 5;
	int *arg = &iteration;

	//create producer thread
	uint* stack1 = (uint*)malloc(64 * sizeof(uint));
	int producerId = thread_create(producer, (void*)stack1, (void*)arg);
	printf(1, "Producer thread %d created at stack 0x%x.\n", producerId, stack1);

	sleep(120);

	//create consumer thread
	uint* stack2 = (uint*)malloc(64 * sizeof(uint));
	int consumerId = thread_create(consumer, (void*)stack2, (void*)arg);
	printf(1, "Consumer thread %d created at stack 0x%x.\n", consumerId, stack2);

	//sleep(1000);

	//wait until all child thread are exit
	uint* stack = (uint*)0;
	int threadId;
	while ((threadId = thread_join((void**)&stack)) != -1) {
		printf(1, "Thread %d finished at stack 0x%x.\n", threadId, *stack);
		free(stack);
	}

	printf(1, "Main function exiting. Buffer size %d\n", buffer.current);
	exit();
	return 0;
}
