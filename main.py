from datetime import date, datetime
from pawpals_system import (
    Owner,
    Pet,
    CareTask,
    TaskRepository,
    Scheduler,
    TaskCategory,
    Frequency,
    DailyConstraints,
    TimeWindow,
    TaskStatus,
    TaskInstance,
)
import uuid

# Create an owner
owner = Owner(name="Sarah", available_minutes_per_day=120)

# Create pets
dog = Pet(
    pet_id=str(uuid.uuid4()),
    name="Max",
    species="dog",
    age_years=3,
    weight_kg=25.0,
    notes="Golden Retriever, loves fetch"
)

cat = Pet(
    pet_id=str(uuid.uuid4()),
    name="Luna",
    species="cat",
    age_years=2,
    weight_kg=4.5,
    notes="Tabby cat, indoor"
)

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Create and populate task repository
task_repo = TaskRepository()

# Add dog tasks intentionally out of chronological order.
dog_midday_med = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=dog.pet_id,
    title="Midday Medication",
    category=TaskCategory.MEDICATION,
    duration_min=10,
    priority=3,
    frequency=Frequency.DAILY,
    preferred_time=TimeWindow(start_hour=12, end_hour=13),
)
dog_morning_walk = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=dog.pet_id,
    title="Morning Walk",
    category=TaskCategory.WALK,
    duration_min=30,
    priority=5,
    frequency=Frequency.DAILY,
    required=True,
    preferred_time=TimeWindow(start_hour=8, end_hour=9),
    notes="Before breakfast",
)
dog_breakfast = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=dog.pet_id,
    title="Breakfast",
    category=TaskCategory.FEEDING,
    duration_min=15,
    priority=4,
    frequency=Frequency.DAILY,
    preferred_time=TimeWindow(start_hour=9, end_hour=10),
)
dog_evening_brush = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=dog.pet_id,
    title="Evening Brush",
    category=TaskCategory.GROOMING,
    duration_min=20,
    priority=2,
    frequency=Frequency.DAILY,
)

# Insert out of order on purpose.
for task in [dog_midday_med, dog_evening_brush, dog_morning_walk, dog_breakfast]:
    task_repo.add_task(task)

# Add one cat task so pet-name filtering can be demonstrated cleanly.
cat_play = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=cat.pet_id,
    title="Cat Feeding and Play",
    category=TaskCategory.ENRICHMENT,
    duration_min=20,
    priority=4,
    frequency=Frequency.DAILY,
    required=True,
)
task_repo.add_task(cat_play)

# Create daily constraints for today
today = date.today()
constraints = DailyConstraints(
    target_date=today,
    available_minutes=120,
    max_tasks=10,
    active_pet_id=dog.pet_id
)

# Generate schedule for the dog
scheduler = Scheduler()
dog_tasks = task_repo.list_tasks_for_pet(dog.pet_id)

print("\n" + "="*60)
print("OUT-OF-ORDER INPUT (DOG TASKS)")
print("="*60)
for task in dog_tasks:
    if task.preferred_time:
        time_label = f"{task.preferred_time.start_hour:02d}:00"
    else:
        time_label = "(no preferred time)"
    print(f"- {task.title:<18} | preferred: {time_label}")

sorted_by_time = scheduler.sort_by_time(dog_tasks)
print("\nSORTED BY TIME (Scheduler.sort_by_time)")
for task in sorted_by_time:
    if task.preferred_time:
        time_label = f"{task.preferred_time.start_hour:02d}:00"
    else:
        time_label = "(no preferred time)"
    print(f"- {task.title:<18} | preferred: {time_label}")

# Create two overlapping task instances at the same start time
# to demonstrate lightweight warning-based conflict detection.
same_time_walk = TaskInstance(
    task=dog_morning_walk,
    scheduled_start=datetime.combine(today, datetime.min.time().replace(hour=8)),
    scheduled_end=datetime.combine(today, datetime.min.time().replace(hour=8, minute=30)),
    reason="Conflict detection demo",
)
same_time_breakfast = TaskInstance(
    task=dog_breakfast,
    scheduled_start=datetime.combine(today, datetime.min.time().replace(hour=8)),
    scheduled_end=datetime.combine(today, datetime.min.time().replace(hour=8, minute=20)),
    reason="Conflict detection demo",
)

conflict_warnings = scheduler.detect_time_conflict_warnings([same_time_walk, same_time_breakfast])
print("\nCONFLICT DETECTION WARNINGS")
if conflict_warnings:
    for warning in conflict_warnings:
        print(f"- {warning}")
else:
    print("- No conflicts detected.")

dog_plan = scheduler.generate_plan(dog_tasks, constraints)

# Mark statuses so we can verify filtering by completion status.
if dog_plan.items:
    dog_plan.items[0].mark_done()
if len(dog_plan.items) > 1:
    dog_plan.items[1].mark_skipped()

print("\n" + "="*60)
print("TODAY'S SCHEDULE FOR MAX (THE DOG)")
print("="*60)
print(dog_plan.summary())
print("\n" + dog_plan.explanation.render_human_readable())
print("="*60 + "\n")

print("FILTERED PLAN ITEMS")
done_items = dog_plan.filter_items(status=TaskStatus.DONE)
skipped_items = dog_plan.filter_items(status=TaskStatus.SKIPPED)
max_items = dog_plan.filter_items(pet_name="Max", pets=owner.pets)

print(f"- DONE items: {[item.task.title for item in done_items]}")
print(f"- SKIPPED items: {[item.task.title for item in skipped_items]}")
print(f"- Items for pet name 'Max': {[item.task.title for item in max_items]}")
print("="*60 + "\n")

# Also generate and display schedule for the cat
constraints.active_pet_id = cat.pet_id
cat_tasks = task_repo.list_tasks_for_pet(cat.pet_id)
cat_plan = scheduler.generate_plan(cat_tasks, constraints)

print("="*60)
print("TODAY'S SCHEDULE FOR LUNA (THE CAT)")
print("="*60)
print(cat_plan.summary())
print("\n" + cat_plan.explanation.render_human_readable())
print("="*60 + "\n")
