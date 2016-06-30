#include "types.h"
#include "x86.h"
#include "defs.h"
#include "param.h"
#include "memlayout.h"
#include "mmu.h"
#include "proc.h"

int
sys_fork(void)
{
  return fork();
}

int
sys_exit(void)
{
  exit();
  return 0;  // not reached
}

int
sys_wait(void)
{
  return wait();
}

int
sys_kill(void)
{
  int pid;

  if(argint(0, &pid) < 0)
    return -1;
  return kill(pid);
}

int
sys_getpid(void)
{
  return proc->pid;
}

int
sys_sbrk(void)
{
  int addr;
  int n;

  if(argint(0, &n) < 0)
    return -1;
  addr = proc->sz;
  if(growproc(n) < 0)
    return -1;
  return addr;
}

int
sys_sleep(void)
{
  int n;
  uint ticks0;
  
  if(argint(0, &n) < 0)
    return -1;
  acquire(&tickslock);
  ticks0 = ticks;
  while(ticks - ticks0 < n){
    if(proc->killed){
      release(&tickslock);
      return -1;
    }
    sleep(&ticks, &tickslock);
  }
  release(&tickslock);
  return 0;
}

// return how many clock tick interrupts have occurred
// since start.
int
sys_uptime(void)
{
  uint xticks;
  
  acquire(&tickslock);
  xticks = ticks;
  release(&tickslock);
  return xticks;
}

/* Machine Problem 1: CPU Bursts */

//Start tracking a CPU burst
int
sys_start_burst(void)
{
	//get current system time tick
	uint xticks = sys_uptime();

	//keep track of current tick as burst start
	proc->burstStart = xticks;

	return xticks;
}

//End tracking a CPU burst
int
sys_end_burst(void)
{
	//get current system time tick
	uint xticks = sys_uptime();

	//calculate cpu burst
	int burst = xticks - proc->burstStart;
	if (burst == 0) return 0;

	//store the burst into array
	int size = sizeof(proc->bursts) / sizeof(int);
	proc->bursts[proc->burstIdx++ % size] = burst;

	return burst;
}

//Print all CPU burst of a process
int
sys_print_bursts(void)
{
	int idx = proc->burstIdx;
	if (idx <= 0) {
		cprintf("There is no CPU bursts yet.\r\n");
		return 0;
	}

	int size = sizeof(proc->bursts) / sizeof(int);
	int i;
	for (i = 0; i < idx; i++) {
		cprintf("%d, ", proc->bursts[i % size]);
	}

	/* Machine Problem 1.3: Modifying the Scheduler */
	int turnaround = sys_uptime() - proc->creationTime;
	cprintf("Turnaround time: %d\r\n", turnaround);

	return idx;
}

/* Machine Problem 2: Kernel Threads */
extern int thread_create(void(*tmain)(void *), void *stack, void *arg);
extern int thread_join(void **stack);
extern int mtx_create(int locked);
extern int mtx_lock(int lock_id);
extern int mtx_unlock(int lock_id);


//Create a new thread
int
sys_thread_create(void)
{
	char* tmain, *stack, *arg;

	if (argptr(0, &tmain, 1) < 0 || argptr(1, &stack, 1) < 0 || argptr(2, &arg, 1) < 0)
		return -1;

	return thread_create((void*)tmain, (void*)stack, (void*)arg);
}

//wait until child thread has been terminated
int
sys_thread_join(void)
{
	char* stack;
	if (argptr(0, &stack, 1) < 0)
		return -1;

	return thread_join((void**)stack);
}

//Creates a mutex lock and returns an opaque ID
int
sys_mtx_create(void)
{
	int locked;
	if (argint(0, &locked) < 0)
		return -1;

	return mtx_create(locked);
}

//Blocks until the lock has been acquired
int
sys_mtx_lock(void)
{
	int lock_id;
	if (argint(0, &lock_id) < 0)
		return -1;

	return mtx_lock(lock_id);
}

//Releases the lock, potentially unblocking a waiting thread
int
sys_mtx_unlock(void)
{
	int lock_id;
	if (argint(0, &lock_id) < 0)
		return -1;

	return mtx_unlock(lock_id);
}