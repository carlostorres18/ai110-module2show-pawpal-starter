# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
    - I included a TaskStatus and this class is able to determine whether a task has been done, is being planned or it has been skipped. Another one i created was a SchedulePlan, this class is responsible of creating and scheduling a task that the user wants to create. A cool class that Copilot suggested was PlannerExplanation, this class is responsible for explaining if a task is able to be created based on the time frame that the user gives to the program so that it can accomodate the created task. Which brings me to the DailyConstraints class, in this class the user is able to tell the program what they have to do during the day that might be a constraint in getting the task for their pet. There are is also the Owner, Pet, TaskCategory, Frequency (how frequent the task is), etc.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
    - So one of the changes that I made to the original design that Copilot suggested for the UML was that the users constraints only included the constraint, but it didn't include the time that said constraint would take, so I prompted Copilot to add a section that in the DailyConstraints class that would allow me the amount of time that would take a user said Constraint that they have to deal with.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
    - My scheduler considers the following: Due-date constraints, in which only tasks due on the target date are considered. Pet-specific constraints, if an active pet is selected, only that pet's tasks are scheduled.

    The way I treated constraints in the following order, feasability first then quality. After that I ranked by time preference and importance so the plan is practical before it is optimized

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
    - One tradeoff is that the planner uses a greedy fit strategy: it schedules tasks in ranked order and skips anything that no longer fits the remaining minutes, rather than searching for the absolute best combination of tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
    - For this project I would use Copilot to design ideas on some of the implementations as well as the algorithmic side of things for the project, specially the part when it came down to making some aspects of the project run faster or not take long as before.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
    - One of the suggestions that took more serious prompting than just the first outputs was when it came down to building the logic and algorithm for the Scheduler. The way that I was able to verify what the AI suggested was that I would tell copilot to implement the changes, test them and see if they are following the guidelines of the project, but also if they made sense overall. If they didn't I would tell Copilot to reverse the changes and then brainstorm another way to make the scheduler, or making changes to the scheduler.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
    - One of the behaviors that I tested was one where I tested recurrence behavior for daily and weekly tasks, verifying that completing a recurring task creates the next scheduled instance with the correct next date and time. These tests reduce the risk of scheduling bugs that could cause missed care tasks, duplicate work, or impossible schedules. Overall making the testing of this application great.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
    - I am confident that my scheduler works correctly for the main use cases because I tested core behaviors like recurring task creation, task ordering, filtering, and time-conflict detection. I would describe this scheduler good, but not perfect as there is always room for improvement, especially high-complexity schedules.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I'm satisfied of the overall structure of the project, this is my first time going as deep as creating the overall design of a new project and how to use AI in a good way for the overall structure of the project.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - If I had another iteration, I would test edge cases where very tight schedules where available minutes are smaller than every task. Or even try to improve the overall structure of how the program behaves.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - It's really Hard!!! But in all seriousness while working with AI may sound enticing on how fast it can create tests or work on the algorithmic side of a project, sometimes AI can lead to decisions that you may think at first is what you wanted to do originally, but would later find that it's not close to what you originally had in mind. So with this in mind we should be aware of code that AI might try to give us so that we can advance on the design of a project as Software Engineers.
