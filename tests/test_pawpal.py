from datetime import datetime

from pawpals_system import (
	CareTask,
	Frequency,
	Pet,
	TaskCategory,
	TaskInstance,
	TaskRepository,
	TaskStatus,
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
