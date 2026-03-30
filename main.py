from datetime import date
from pawpals_system import (
    Owner, Pet, CareTask, TaskRepository, Scheduler, 
    TaskCategory, Frequency, DailyConstraints
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

# Task 1: Morning walk for dog
morning_walk = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=dog.pet_id,
    title="Morning Walk",
    category=TaskCategory.WALK,
    duration_min=30,
    priority=5,
    frequency=Frequency.DAILY,
    required=True,
    notes="Before breakfast"
)
task_repo.add_task(morning_walk)

# Task 2: Dog feeding
dog_feeding = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=dog.pet_id,
    title="Dog Feeding",
    category=TaskCategory.FEEDING,
    duration_min=15,
    priority=5,
    frequency=Frequency.DAILY,
    required=True,
    notes="Two meals per day"
)
task_repo.add_task(dog_feeding)

# Task 3: Cat feeding and play
cat_play = CareTask(
    task_id=str(uuid.uuid4()),
    pet_id=cat.pet_id,
    title="Cat Feeding and Play",
    category=TaskCategory.ENRICHMENT,
    duration_min=20,
    priority=4,
    frequency=Frequency.DAILY,
    required=True,
    notes="Interactive play session"
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
dog_plan = scheduler.generate_plan(dog_tasks, constraints)

# Print today's schedule for the dog
print("\n" + "="*60)
print("TODAY'S SCHEDULE FOR MAX (THE DOG)")
print("="*60)
print(dog_plan.summary())
print("\n" + dog_plan.explanation.render_human_readable())
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
