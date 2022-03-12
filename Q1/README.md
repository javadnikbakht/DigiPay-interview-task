# Java Memory Management

## Introduction
Thanks in advance for reading this article. This article is very long. On the Internet, and there are definitely a lot of good resources s about memory leaks, JVM Architecture, so on. I hope this article be useful from my readings and information.


In this article I write somthing about these topics:

* Java Virtual Machine Architecture (JVM Architecture)
* Memory Model (HEAP, Non-HEAP, Other Memory)
* Garbage Collection
* Monitoring & GC Tuning


At first I should say in Java we have Garbage Collection. Garbage Collection is the process by which Java programs perform automatic memory management. Basically, for example if you write a code by Java/Kotlin will compile to byte code (.class file) and run on Java Virtual Machine(JVM). When the application runs on JVM, the most of objects are created on HEAP memory. Eventually, some objects will no longer be needed(unreachable/unuse objects). The Garbage Collector will reclaim unuse memory to recover memory for Application, other Applications, Operating System.

> In other words: “Memory management is the process of allocating new objects and removing unused objects to make space for those new object allocations” [source](https://docs.oracle.com/cd/E13150_01/jrockit_jvm/jrockit/geninfo/diagnos/garbage_collect.html)


In some languages like C, we have to manage memory manually. Thus, write the application by C is very difficult. We have to allocate/deallocate variables, objects carefully because It can leak memory.


Eventually, I think that manage memory is very important for every developer. It doesn’t depend on programming language: Java/C, … Understanding deeper in manage memory will help you write a good application with high performance and can run on low profile machines. Basically, our application will run on JVM. So, we should understanding JVM Architecture first.

## Java Virtual Machine Architecture (JVM Architecture)

JVM is only a specification and it has many different implementations. You can mapping with an interface and many implements in your code. To know JVM information you can run the command `$ java -version` on the terminal and its better to user Oracle JDK. It’s very stable and focuses on enterprise applications. So, In this article, I will only write about it.

There are many articles write about it we can search on the internet. one of articles I've read is https://medium.com/platform-engineer/understanding-jvm-architecture-22c0ddf09722

![Source Image: PlatformEngineer.com](https://miro.medium.com/max/1286/1*CPWV-1FlOk-7SNoNWzM5cA.png)

I will summarize some points from the above article:

1. **Class Loader Subsystem** : JVM resides on the RAM. During execution, using the Class Loader Subsystem, the class files are brought on to the RAM. This is called Java’s dynamic class loading functionality. It loads, links, and initializes the class file (.class) when it refers to a class for the first time at runtime. Finally, initialization logic of each loaded class will be executed(eg. calling the constructor of a class), all static variables will be assigned original values & static block gets executed.

1. **Runtime Data Area** : the memory areas assigned when the JVM program runs on the OS

* **Method Area** (shared among threads). Sometimes, we can call it by Class Area because it will store all the class level data (run time constant pool, static variables, field data, methods (data, code)). Only one method area per JVM.

* **Heap Area** (shared among threads): all the variables, objects, arrays will store in here. One Heap per JVM. The Heap area is a great target for GC.

* **Stack Area** (per thread): For every thread new stack at runtime will be created, for every method call, one entry will be added in the stack called a stack frame. Each stack frame has the reference for the local variable array, operand stack, and runtime constant pool of a class where the method being executed belongs.

3. **Execution Engine** : The byte code which is assigned in Runtime data are will be executed.

* **Interpreter**: Interprets the bytecode faster but execution slowly. The disadvantage is that when one method is called multiple times, each time a new interpretation and a slower execution are required.

* **JIT Compiler**: solve the disadvantage of the interpreter whenever it finds repeated code it uses JIT Compiler. It will compile the bytecode into native code(machine code). The native code is stored in the cache, thus the compiled code can be executed quicker.

* **Garbage Collector**: collects and removes unreferenced objects. As long as an object is being referenced, the JVM considers it alive. Once an object is no longer referenced and therefore is not reachable by the application code, the garbage collector removes it and reclaims the unused memory. In general, the garbage collector is an automatic process. However, we can trigger it by calling System.gc() or Runtime.getRuntime().gc() method (Again the execution is not guaranteed. Hence, call Thread.sleep(1000) and wait for GC to complete).

### Memory Model (HEAP, Non-HEAP, Other Memory)

The JVM consumes the available memory space on the Operating System. The JVM includes memory areas: HEAP, Non-HEAP, and Other Memory.

![Overview Memory Model](https://miro.medium.com/max/1400/1*EodMkw9QoqApxvxF_5ROOA.png)


1. **HEAP**: includes two parts: Young Generation (Young Gen) and Old Generation (Old Gen).

![Source: PlatformEngineer.com](https://miro.medium.com/max/1400/1*iQmXAWwi1ddSa8mZhruRGA.png)

**1.1 Young Generation**: all the new objects are created in here. When the young generation is filled, the Garbage collector (Minor GC) is performed. It’s divided into three parts: one Eden Space and two Survivor Spaces(S0, S1). Some points in the young generation:
* Most of the newly created objects are located in the Eden Space.
* If Eden space is filled with objects, Minor GC is performed and all survivor objects are moved to one of the survivor spaces.

* Objects that are survived after many cycles of Minor GC are moved to Old Generation space. Usually, it’s done by setting a threshold for the age of the young generation objects before they become eligible to promote to the old generation.

**1.2 Old Generation**: This is reserved for containing long-lived objects that survive after many rounds of Minor GC. When the old generation is full, Major GC is performed (usually takes longer time).


2.**Non-HEAP (Off-HEAP)**: Sometimes, we call it by name Off-HEAP. With Java 7 and earlier this space is called by Permanent Generation(`Perm Gen`). Since Java 8, Perm Gen is replaced by Metaspace. Nowadays, we won’t use Java 7 anymore because Java 8 is released in 2014 with many improvements. Besides, we have Java 11 LTS.

Metaspace stores per-class structures such as runtime constant pool, field and method data, and the code of methods and constructors, as well as interned Strings.

Metaspace by default auto increases its size (up to what the underlying OS provides), while Perm Gen always has a fixed maximum size. Two news flags can be used to set the size of the metaspace: “-XX:MetaspaceSize” and “-XX:MaxMetaspaceSize”.

3. **Other Memory**

3.1 **CodeCache** contains complied code (i.e native code) generate by JIT compiler, JVM internal structures, loaded profiler agent code, and data, etc.

3.2 **Thread Stacks** refer to the interpreted, compiled, and native stack frames.

3.3 **Direct Memory** is used by direct-buffer allocations (e.g NIO Buffer/ByteBuffer)

3.4 **C-Heap** is used for example, by the JIT Compiler or by the GC to allocate memory for internal data structures.


## Garbage Collection

Like what I told before, GC helps developers write code without allocation/deallocation memory and don’t care about memory issues. However, In the actual project, we have many memory issues. They make your application run low performance and very slow.

Thus, we should understand how GC works. All objects are allocated on the heap managed by the JVM. As long as an object is being referenced, the JVM considers it alive. Once an object is no longer referenced and therefore is not reachable by the application code, the garbage collector obremoves it and reclaims the unused memory.

How to GC manage objects in HEAP? The answer is it will build a Tree called Garbage Collection Roots (GC roots). It contains many references between application code and objects in HEAP. There are four types of GC roots: Local variables, Active java threads, Static variables, JNI references. **As long as our object is directly or indirectly referenced by one of these GC roots and the GC root remains alive, our object can be considered as a reachable object. The moment our object loses its reference to a GC root, it becomes unreachable, hence eligible for the GC.**


![image](https://miro.medium.com/max/918/1*ZJFBfrxntb6hU73FBE317Q.png)


#### Mark and Sweep Model

To determine which objects are no longer in use, JVM uses the mark-and-sweep algorithm.

* The algorithm traverses all object references, starting with the GC roots, and marks every object found as alive.
* All of the heap memory that is not occupied by marked objects is claimed.

It’s possible to have unused objects that are still reachable by an application because developers simply forgot to dereference them. This case makes memory leak. So, you have to monitor/analyze your application to spot the problem.

![image](https://miro.medium.com/max/1400/1*oRJWagRPy8_Wj98TN2pZ9w.png)

#### Stop the World Event

When GC performed, all application threads are stopped until the operation completes. Since Young Generation keeps short-lived objects, Minor GC is very fast and the application doesn’t get affected by this. However, Major GC takes a long time because it checks all the live objects. Major GC should be minimized because it will make your application unresponsive for the GC duration.


### Monitoring & GC Tuning

We can monitor the java application by command line and tools. In fact, there are many tools: JVisualVM, JProfile, Eclipse MAT, JetBrains JVM Debugger, Netbeans Profiler, … I personally recommend you use JVisualVM which built-in JDK. It’s enough good for monitoring your application.

Jstat we can use jstat command line tool to monitor the JVM Memory and GC activities. Example: `jstat -gc <pid> 1000` (print memory and GC data every 1 second)


![image](https://miro.medium.com/max/1400/1*ICgutfMQ2SI2iCDn0cFPbg.png)


![image](https://miro.medium.com/max/1400/1*VgKUgxciWOkLdjJyhZWTkg.png)




**JVisualVM** we can open GUI Tool via Terminal with command “jvisualvm”. I have used this tool to make an example at the beginning of this article. I personally recommend using JVisualVM for Monitoring/GC Tuning when we before releasing any features on the beta/staging/production environment. You should check memory issues to:

* Guarantee your application consumes less memory possible.
* Guarantee your application runs very fast and no problems with memory leaks.

**Notice that your application can use native memory (Metaspace, Direct Memory) which isn’t the target of GC. In that case, you have to allocate/deallocate memory manually. When you use 3-rd party library, you should check carefully before using them**. My team had a problem with 3-rd party library when we integrated it into my project. We thought it will use HEAP and create multi-instance in our application but actually it uses direct memory (ByteBuffer). When we deploy our application to the server on the beta environment, everything works ok!!. After we do performance testing with Jmeter, we have got an error: Out of memory (Memory Leak).

### Java Non-Standard Options

To improve performance for your application. You should check and set java non-standard options appropriately. You can view non-standard options via command line: `java -X`. Pls, take a lock at:

![image](https://miro.medium.com/max/1298/1*BLWVNht1LWD-HYIlSmLhXA.png)





### References

* https://medium.com/platform-engineer/understanding-jvm-architecture-22c0ddf09722

* https://medium.com/platform-engineer/understanding-java-garbage-collection-54fc9230659a

* https://betsol.com/java-memory-management-for-java-virtual-machine-jvm

* https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/index.html

* https://www.dynatrace.com/resources/ebooks/javabook/how-garbage-collection-works/

