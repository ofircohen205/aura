---
title: "Multithreading"
language: java
difficulty: advanced
prerequisites: ["Classes", "Interfaces"]
keywords: [threads, multithreading, concurrency, Runnable, Thread, synchronized, ExecutorService]
---

# Learning Objectives

- Understand threads and multithreading
- Create and manage threads
- Use Runnable and Thread
- Understand thread synchronization
- Work with ExecutorService
- Handle thread safety issues

# Prerequisites

- Classes
- Interfaces

# Introduction

Multithreading allows your program to execute multiple tasks concurrently. Java provides comprehensive support for multithreading through threads, executors, and synchronization mechanisms. Understanding multithreading is essential for building responsive, efficient applications.

# Core Concepts

## Creating Threads

### Using Thread Class

```java
class MyThread extends Thread {
    public void run() {
        System.out.println("Thread is running");
    }
}

MyThread thread = new MyThread();
thread.start();
```

### Using Runnable Interface

```java
class MyTask implements Runnable {
    public void run() {
        System.out.println("Task is running");
    }
}

Thread thread = new Thread(new MyTask());
thread.start();

// Or with lambda
Thread thread2 = new Thread(() -> System.out.println("Lambda task"));
thread2.start();
```

## Thread Lifecycle

```java
Thread thread = new Thread(() -> {
    try {
        Thread.sleep(1000);
        System.out.println("Thread completed");
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
});

thread.start();  // Start thread
// Thread goes through: NEW -> RUNNABLE -> RUNNING -> TERMINATED
```

## Synchronization

Prevent race conditions:

```java
class Counter {
    private int count = 0;

    public synchronized void increment() {
        count++;
    }

    public synchronized int getCount() {
        return count;
    }
}

// Or use synchronized blocks
public void method() {
    synchronized (this) {
        // Critical section
    }
}
```

## ExecutorService

Better way to manage threads:

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

ExecutorService executor = Executors.newFixedThreadPool(5);

for (int i = 0; i < 10; i++) {
    executor.submit(() -> {
        System.out.println("Task executed by: " + Thread.currentThread().getName());
    });
}

executor.shutdown();
```

## Future and Callable

Get results from threads:

```java
import java.util.concurrent.*;

ExecutorService executor = Executors.newSingleThreadExecutor();

Future<Integer> future = executor.submit(() -> {
    Thread.sleep(1000);
    return 42;
});

try {
    Integer result = future.get();  // Waits for result
    System.out.println("Result: " + result);
} catch (ExecutionException | InterruptedException e) {
    e.printStackTrace();
}
```

# Common Mistakes

- **Race conditions**: Not synchronizing shared data
- **Deadlocks**: Circular waiting for locks
- **Creating too many threads**: Use thread pools
- **Not shutting down ExecutorService**: Can prevent program exit
- **Ignoring InterruptedException**: Should handle properly

# Practice Exercises

1. Create a thread using Runnable and start it.
2. Create multiple threads and observe concurrent execution.
3. Use synchronization to prevent race conditions in a counter.
4. Use ExecutorService to execute multiple tasks.
5. Use Future to get results from asynchronous tasks.

Example solution for exercise 1:

```java
Runnable task = () -> {
    for (int i = 0; i < 5; i++) {
        System.out.println(Thread.currentThread().getName() + ": " + i);
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
};

Thread thread = new Thread(task);
thread.start();
```

# Key Takeaways

- Threads enable concurrent execution
- Use Runnable interface or extend Thread
- Synchronization prevents race conditions
- Use `synchronized` keyword or blocks
- ExecutorService manages thread pools efficiently
- Future and Callable get results from threads
- Multithreading requires careful handling of shared data
- Use thread pools instead of creating many threads

# Related Topics

- Classes (Java Intermediate #1)
- Interfaces (Java Intermediate #5)
- Exception Handling (Java Intermediate #6)
