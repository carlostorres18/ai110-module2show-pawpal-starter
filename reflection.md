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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
