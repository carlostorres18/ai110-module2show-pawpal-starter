from datetime import date, datetime, timedelta

from pawpals_system import (
	CareTask,
	DailyConstraints,
	Frequency,
	Owner,
	Pet,
	SchedulePlan,
	Scheduler,
	TaskCategory,
	TaskInstance,
	TaskRepository,
	TaskStatus,
	TimeWindow,
	Weekday,
)


def test_task_completion_changes_status() -> None:
	pet = Pet(
		pet_id="pet-1",
		name="Mochi",
		species="dog",
		age_years=2,
		weight_kg=8.5,
	)
	task = CareTask(
		task_id="task-1",
		pet_id=pet.pet_id,
		title="Morning walk",
		category=TaskCategory.WALK,
		duration_min=20,
		priority=3,
		frequency=Frequency.DAILY,
	)
	instance = TaskInstance(
		task=task,
		scheduled_start=datetime(2026, 1, 1, 8, 0),
		scheduled_end=datetime(2026, 1, 1, 8, 20),
		reason="daily care",
	)

	instance.mark_done()

	assert instance.status == TaskStatus.DONE


def test_mark_done_creates_next_daily_instance() -> None:
	task = CareTask(
		task_id="task-daily",
		pet_id="pet-1",
		title="Daily feeding",
		category=TaskCategory.FEEDING,
		duration_min=15,
		priority=4,
		frequency=Frequency.DAILY,
	)
	instance = TaskInstance(
		task=task,
		scheduled_start=datetime(2026, 3, 29, 8, 0),
		scheduled_end=datetime(2026, 3, 29, 8, 15),
		reason="daily care",
	)

	next_instance = instance.mark_done()

	assert instance.status == TaskStatus.DONE
	assert next_instance is not None
	assert next_instance.task.frequency == Frequency.DAILY
	assert next_instance.task.task_id != task.task_id
	assert next_instance.task.due_date == date.today() + timedelta(days=1)
	assert next_instance.scheduled_start == datetime(2026, 3, 30, 8, 0)
	assert next_instance.scheduled_end == datetime(2026, 3, 30, 8, 15)


def test_mark_done_creates_next_weekly_instance() -> None:
	task = CareTask(
		task_id="task-weekly",
		pet_id="pet-1",
		title="Weekly grooming",
		category=TaskCategory.GROOMING,
		duration_min=30,
		priority=3,
		frequency=Frequency.WEEKLY,
	)
	instance = TaskInstance(
		task=task,
		scheduled_start=datetime(2026, 3, 29, 10, 0),
		scheduled_end=datetime(2026, 3, 29, 10, 30),
		reason="weekly care",
	)

	next_instance = instance.mark_done()

	assert instance.status == TaskStatus.DONE
	assert next_instance is not None
	assert next_instance.task.frequency == Frequency.WEEKLY
	assert next_instance.task.task_id != task.task_id
	assert next_instance.task.due_date == date.today() + timedelta(weeks=1)
	assert next_instance.scheduled_start == datetime(2026, 4, 5, 10, 0)
	assert next_instance.scheduled_end == datetime(2026, 4, 5, 10, 30)


def test_adding_task_for_pet_increases_task_count() -> None:
	pet = Pet(
		pet_id="pet-2",
		name="Luna",
		species="cat",
		age_years=3,
		weight_kg=4.2,
	)
	repo = TaskRepository()
	starting_count = len(repo.list_tasks_for_pet(pet.pet_id))
	task = CareTask(
		task_id="task-2",
		pet_id=pet.pet_id,
		title="Feed dinner",
		category=TaskCategory.FEEDING,
		duration_min=10,
		priority=4,
		frequency=Frequency.DAILY,
	)

	repo.add_task(task)

	assert len(repo.list_tasks_for_pet(pet.pet_id)) == starting_count + 1


def test_scheduler_rank_tasks_orders_by_time_then_tiebreakers() -> None:
	scheduler = Scheduler()
	constraints = DailyConstraints(
		target_date=date(2026, 3, 30),
		available_minutes=120,
		max_tasks=5,
		active_pet_id="pet-1",
	)
	tasks = [
		CareTask(
			task_id="task-c",
			pet_id="pet-1",
			title="Midday meds",
			category=TaskCategory.MEDICATION,
			duration_min=10,
			priority=2,
			frequency=Frequency.DAILY,
			preferred_time=TimeWindow(start_hour=12, end_hour=13),
		),
		CareTask(
			task_id="task-a",
			pet_id="pet-1",
			title="Morning walk",
			category=TaskCategory.WALK,
			duration_min=20,
			priority=1,
			frequency=Frequency.DAILY,
			preferred_time=TimeWindow(start_hour=8, end_hour=9),
		),
		CareTask(
			task_id="task-b",
			pet_id="pet-1",
			title="Breakfast",
			category=TaskCategory.FEEDING,
			duration_min=15,
			priority=5,
			frequency=Frequency.DAILY,
		),
	]

	ranked = scheduler.rank_tasks(tasks, constraints)

	assert [task.task_id for task in ranked] == ["task-a", "task-c", "task-b"]


def test_task_repository_filter_pipeline_applies_all_criteria() -> None:
	repo = TaskRepository()
	task_due_for_pet = CareTask(
		task_id="task-1",
		pet_id="pet-1",
		title="Dinner",
		category=TaskCategory.FEEDING,
		duration_min=10,
		priority=3,
		frequency=Frequency.DAILY,
	)
	task_wrong_category = CareTask(
		task_id="task-2",
		pet_id="pet-1",
		title="Evening walk",
		category=TaskCategory.WALK,
		duration_min=20,
		priority=2,
		frequency=Frequency.DAILY,
	)
	task_not_due = CareTask(
		task_id="task-3",
		pet_id="pet-1",
		title="Weekly grooming",
		category=TaskCategory.FEEDING,
		duration_min=25,
		priority=1,
		frequency=Frequency.WEEKLY,
		weekdays={Weekday.SUNDAY},
	)
	task_other_pet = CareTask(
		task_id="task-4",
		pet_id="pet-2",
		title="Dinner",
		category=TaskCategory.FEEDING,
		duration_min=10,
		priority=3,
		frequency=Frequency.DAILY,
	)

	for task in [task_due_for_pet, task_wrong_category, task_not_due, task_other_pet]:
		repo.add_task(task)

	filtered = repo.filter_tasks(
		pet_id="pet-1",
		category=TaskCategory.FEEDING,
		due_date=date(2026, 3, 30),
	)

	assert [task.task_id for task in filtered] == ["task-1"]


def test_schedule_plan_filter_items_by_status_or_pet_name() -> None:
	owner = Owner(name="Jordan")
	dog = Pet(
		pet_id="pet-dog",
		name="Mochi",
		species="dog",
		age_years=2,
		weight_kg=8.5,
	)
	cat = Pet(
		pet_id="pet-cat",
		name="Luna",
		species="cat",
		age_years=3,
		weight_kg=4.2,
	)
	owner.add_pet(dog)
	owner.add_pet(cat)

	dog_task = CareTask(
		task_id="task-dog",
		pet_id=dog.pet_id,
		title="Morning walk",
		category=TaskCategory.WALK,
		duration_min=20,
		priority=3,
		frequency=Frequency.DAILY,
	)
	cat_task = CareTask(
		task_id="task-cat",
		pet_id=cat.pet_id,
		title="Cat feeding",
		category=TaskCategory.FEEDING,
		duration_min=10,
		priority=4,
		frequency=Frequency.DAILY,
	)

	dog_instance = TaskInstance(
		task=dog_task,
		scheduled_start=datetime(2026, 3, 30, 8, 0),
		scheduled_end=datetime(2026, 3, 30, 8, 20),
		reason="daily care",
	)
	cat_instance = TaskInstance(
		task=cat_task,
		scheduled_start=datetime(2026, 3, 30, 9, 0),
		scheduled_end=datetime(2026, 3, 30, 9, 10),
		reason="daily care",
	)
	cat_instance.mark_done()

	plan = SchedulePlan(plan_date=date(2026, 3, 30), items=[dog_instance, cat_instance])

	planned_items = plan.filter_items(status=TaskStatus.PLANNED)
	assert [item.task.task_id for item in planned_items] == ["task-dog"]

	mochi_items = plan.filter_items(pet_name="Mochi", pets=owner.pets)
	assert [item.task.task_id for item in mochi_items] == ["task-dog"]


def test_scheduler_detects_conflicts_for_same_pet() -> None:
	scheduler = Scheduler()
	pet_id = "pet-1"

	first_task = CareTask(
		task_id="task-1",
		pet_id=pet_id,
		title="Morning walk",
		category=TaskCategory.WALK,
		duration_min=30,
		priority=3,
		frequency=Frequency.DAILY,
	)
	second_task = CareTask(
		task_id="task-2",
		pet_id=pet_id,
		title="Breakfast",
		category=TaskCategory.FEEDING,
		duration_min=15,
		priority=4,
		frequency=Frequency.DAILY,
	)

	first_instance = TaskInstance(
		task=first_task,
		scheduled_start=datetime(2026, 3, 30, 8, 0),
		scheduled_end=datetime(2026, 3, 30, 8, 30),
		reason="daily care",
	)
	second_instance = TaskInstance(
		task=second_task,
		scheduled_start=datetime(2026, 3, 30, 8, 0),
		scheduled_end=datetime(2026, 3, 30, 8, 15),
		reason="daily care",
	)

	conflicts = scheduler.detect_time_conflicts([first_instance, second_instance])

	assert len(conflicts) == 1
	left, right = conflicts[0]
	assert {left.task.task_id, right.task.task_id} == {"task-1", "task-2"}


def test_scheduler_detects_conflicts_for_different_pets() -> None:
	scheduler = Scheduler()

	dog_task = CareTask(
		task_id="task-dog",
		pet_id="pet-dog",
		title="Dog walk",
		category=TaskCategory.WALK,
		duration_min=20,
		priority=3,
		frequency=Frequency.DAILY,
	)
	cat_task = CareTask(
		task_id="task-cat",
		pet_id="pet-cat",
		title="Cat feeding",
		category=TaskCategory.FEEDING,
		duration_min=10,
		priority=4,
		frequency=Frequency.DAILY,
	)

	dog_instance = TaskInstance(
		task=dog_task,
		scheduled_start=datetime(2026, 3, 30, 9, 0),
		scheduled_end=datetime(2026, 3, 30, 9, 20),
		reason="daily care",
	)
	cat_instance = TaskInstance(
		task=cat_task,
		scheduled_start=datetime(2026, 3, 30, 9, 0),
		scheduled_end=datetime(2026, 3, 30, 9, 10),
		reason="daily care",
	)

	conflicts = scheduler.detect_time_conflicts([dog_instance, cat_instance])

	assert len(conflicts) == 1
	left, right = conflicts[0]
	assert {left.task.pet_id, right.task.pet_id} == {"pet-dog", "pet-cat"}


def test_scheduler_detect_time_conflicts_returns_empty_when_no_overlap() -> None:
	scheduler = Scheduler()

	first_task = CareTask(
		task_id="task-1",
		pet_id="pet-1",
		title="Morning walk",
		category=TaskCategory.WALK,
		duration_min=20,
		priority=3,
		frequency=Frequency.DAILY,
	)
	second_task = CareTask(
		task_id="task-2",
		pet_id="pet-2",
		title="Evening feeding",
		category=TaskCategory.FEEDING,
		duration_min=15,
		priority=4,
		frequency=Frequency.DAILY,
	)

	first_instance = TaskInstance(
		task=first_task,
		scheduled_start=datetime(2026, 3, 30, 8, 0),
		scheduled_end=datetime(2026, 3, 30, 8, 20),
		reason="daily care",
	)
	second_instance = TaskInstance(
		task=second_task,
		scheduled_start=datetime(2026, 3, 30, 8, 20),
		scheduled_end=datetime(2026, 3, 30, 8, 35),
		reason="daily care",
	)

	conflicts = scheduler.detect_time_conflicts([first_instance, second_instance])

	assert conflicts == []


def test_scheduler_lightweight_conflict_detection_returns_warning_message() -> None:
	scheduler = Scheduler()

	first_task = CareTask(
		task_id="task-1",
		pet_id="pet-1",
		title="Morning walk",
		category=TaskCategory.WALK,
		duration_min=20,
		priority=3,
		frequency=Frequency.DAILY,
	)
	second_task = CareTask(
		task_id="task-2",
		pet_id="pet-2",
		title="Cat feeding",
		category=TaskCategory.FEEDING,
		duration_min=10,
		priority=4,
		frequency=Frequency.DAILY,
	)

	first_instance = TaskInstance(
		task=first_task,
		scheduled_start=datetime(2026, 3, 30, 9, 0),
		scheduled_end=datetime(2026, 3, 30, 9, 20),
		reason="daily care",
	)
	second_instance = TaskInstance(
		task=second_task,
		scheduled_start=datetime(2026, 3, 30, 9, 0),
		scheduled_end=datetime(2026, 3, 30, 9, 10),
		reason="daily care",
	)

	warnings = scheduler.detect_time_conflict_warnings([first_instance, second_instance])

	assert len(warnings) == 1
	assert "Warning:" in warnings[0]
	assert "Morning walk" in warnings[0]
	assert "Cat feeding" in warnings[0]


def test_scheduler_lightweight_conflict_detection_handles_invalid_windows() -> None:
	scheduler = Scheduler()
	task = CareTask(
		task_id="task-invalid",
		pet_id="pet-1",
		title="Invalid window task",
		category=TaskCategory.OTHER,
		duration_min=15,
		priority=1,
		frequency=Frequency.DAILY,
	)

	invalid_instance = TaskInstance(
		task=task,
		scheduled_start=None,
		scheduled_end=datetime(2026, 3, 30, 10, 0),
		reason="bad data",
	)

	warnings = scheduler.detect_time_conflict_warnings([invalid_instance])

	assert len(warnings) == 1
	assert "Warning:" in warnings[0]
	assert "invalid time window" in warnings[0]
