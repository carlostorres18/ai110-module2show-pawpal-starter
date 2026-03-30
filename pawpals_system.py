from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any
import uuid
from copy import deepcopy


class TaskCategory(Enum):
	WALK = "walk"
	FEEDING = "feeding"
	MEDICATION = "medication"
	ENRICHMENT = "enrichment"
	GROOMING = "grooming"
	HYGIENE = "hygiene"
	TRAINING = "training"
	OTHER = "other"


class Frequency(Enum):
	DAILY = "daily"
	WEEKLY = "weekly"
	CUSTOM = "custom"


class Weekday(Enum):
	MONDAY = "monday"
	TUESDAY = "tuesday"
	WEDNESDAY = "wednesday"
	THURSDAY = "thursday"
	FRIDAY = "friday"
	SATURDAY = "saturday"
	SUNDAY = "sunday"


class TaskStatus(Enum):
	PLANNED = "planned"
	DONE = "done"
	SKIPPED = "skipped"


@dataclass
class TimeWindow:
	start_hour: int
	end_hour: int

	def contains(self, hour: int) -> bool:
		"""Check if the given hour falls within this time window."""
		return self.start_hour <= hour < self.end_hour


@dataclass
class Owner:
	name: str
	preferences: dict[str, Any] = field(default_factory=dict)
	available_minutes_per_day: int = 0
	pets: list[Pet] = field(default_factory=list)
	default_pet_id: str | None = None

	def add_preference(self, key: str, value: Any) -> None:
		"""Store a preference in the preferences dictionary."""
		self.preferences[key] = value

	def get_preference(self, key: str) -> Any:
		"""Retrieve a preference value by key, return None if not found."""
		return self.preferences.get(key)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to the owner's pet list and set as default if first."""
		self.pets.append(pet)
		if self.default_pet_id is None and len(self.pets) == 1:
			self.default_pet_id = pet.pet_id

	def get_default_pet(self) -> Pet | None:
		"""Return the default pet, or the only pet if one exists."""
		if self.default_pet_id is not None:
			for pet in self.pets:
				if pet.pet_id == self.default_pet_id:
					return pet
		# Fallback: if exactly one pet and no default set, return it
		if len(self.pets) == 1:
			return self.pets[0]
		return None


@dataclass
class Pet:
	pet_id: str
	name: str
	species: str
	age_years: int
	weight_kg: float
	notes: str = ""


@dataclass
class CareTask:
	task_id: str
	pet_id: str
	title: str
	category: TaskCategory
	duration_min: int
	priority: int
	frequency: Frequency
	weekdays: set[Weekday] = field(default_factory=set)
	due_date: date = field(default_factory=date.today)
	required: bool = False
	preferred_time: TimeWindow | None = None
	notes: str = ""

	def is_due(self, target_date: date) -> bool:
		"""Return whether this task is due on the target date."""
		if self.frequency == Frequency.DAILY:
			return True
		
		if self.frequency in (Frequency.WEEKLY, Frequency.CUSTOM):
			# Map Python's weekday (0=Monday, 6=Sunday) to our Weekday enum
			weekday_name = target_date.strftime("%A").lower()
			weekday_enum = Weekday[weekday_name.upper()]
			return weekday_enum in self.weekdays
		
		return False

	def score(self, constraints: DailyConstraints) -> float:
		"""Calculate a scheduling score based on task priority and required status."""
		base_score = float(self.priority)
		if self.required:
			base_score *= 1.5
		return base_score


@dataclass
class DailyConstraints:
	target_date: date
	available_minutes: int
	max_tasks: int
	active_pet_id: str | None = None
	blocked_windows: list[TimeWindow] = field(default_factory=list)
	energy_level: int = 5

	def validate(self) -> bool:
		"""Check that constraints are sensible: available_minutes and max_tasks both positive."""
		return self.available_minutes > 0 and self.max_tasks > 0


@dataclass
class TaskInstance:
	task: CareTask
	scheduled_start: datetime
	scheduled_end: datetime
	reason: str
	status: TaskStatus = TaskStatus.PLANNED

	def mark_done(self) -> TaskInstance | None:
		"""Mark this task instance as completed and return next recurring instance when applicable."""
		self.status = TaskStatus.DONE
		if self.task.frequency == Frequency.DAILY:
			next_due = date.today() + timedelta(days=1)
			return self._build_next_instance(next_due, timedelta(days=1))

		if self.task.frequency == Frequency.WEEKLY:
			next_due = date.today() + timedelta(weeks=1)
			return self._build_next_instance(next_due, timedelta(weeks=1))

		return None

	def _build_next_instance(self, due_date: date, schedule_delta: timedelta) -> TaskInstance:
		"""Create the next recurring task instance with an updated due date."""
		next_task = deepcopy(self.task)
		next_task.task_id = str(uuid.uuid4())
		next_task.due_date = due_date

		return TaskInstance(
			task=next_task,
			scheduled_start=self.scheduled_start + schedule_delta,
			scheduled_end=self.scheduled_end + schedule_delta,
			reason="Auto-created from recurring task completion.",
		)

	def mark_skipped(self) -> None:
		"""Mark this task instance as skipped."""
		self.status = TaskStatus.SKIPPED


@dataclass
class SchedulePlan:
	plan_date: date
	items: list[TaskInstance] = field(default_factory=list)
	total_minutes: int = 0
	unscheduled_tasks: list[CareTask] = field(default_factory=list)
	warnings: list[str] = field(default_factory=list)
	explanation: PlannerExplanation | None = None

	def filter_items(
		self,
		status: TaskStatus | None = None,
		pet_name: str | None = None,
		pets: list[Pet] | None = None,
	) -> list[TaskInstance]:
		"""Filter scheduled items by completion status and/or pet name."""
		filtered = list(self.items)

		if status is not None:
			filtered = [item for item in filtered if item.status == status]

		if pet_name is not None:
			matching_pet_ids: set[str]
			if pets is not None:
				normalized_pet_name = pet_name.strip().lower()
				matching_pet_ids = {
					pet.pet_id for pet in pets if pet.name.strip().lower() == normalized_pet_name
				}
			else:
				matching_pet_ids = {pet_name}

			filtered = [item for item in filtered if item.task.pet_id in matching_pet_ids]

		return filtered

	def add_item(self, item: TaskInstance) -> None:
		"""Add a task instance to the schedule and update total_minutes."""
		self.items.append(item)
		duration = int((item.scheduled_end - item.scheduled_start).total_seconds() / 60)
		self.total_minutes += duration

	def remove_item(self, task_id: str) -> None:
		"""Remove a task instance by task_id and update total_minutes."""
		for i, item in enumerate(self.items):
			if item.task.task_id == task_id:
				duration = int((item.scheduled_end - item.scheduled_start).total_seconds() / 60)
				self.total_minutes -= duration
				self.items.pop(i)
				return

	def summary(self) -> str:
		"""Return a human-readable summary of the plan."""
		lines = [f"Daily Plan for {self.plan_date}"]
		lines.append(f"Total scheduled time: {self.total_minutes} minutes")
		lines.append(f"Tasks scheduled: {len(self.items)}")
		
		if self.items:
			lines.append("\nScheduled tasks:")
			for item in self.items:
				lines.append(f"  - {item.task.title} ({item.task.duration_min} min) at {item.scheduled_start.strftime('%H:%M')}")
		
		if self.unscheduled_tasks:
			lines.append(f"\nCould not fit {len(self.unscheduled_tasks)} tasks:")
			for task in self.unscheduled_tasks:
				lines.append(f"  - {task.title} ({task.duration_min} min)")

		if self.warnings:
			lines.append("\nWarnings:")
			for warning in self.warnings:
				lines.append(f"  - {warning}")
		
		return "\n".join(lines)


@dataclass
class PlannerExplanation:
	selected_reasons: dict[str, str] = field(default_factory=dict)
	unscheduled_reasons: dict[str, str] = field(default_factory=dict)

	def render_human_readable(self) -> str:
		"""Render the explanation as a readable text block."""
		lines = []
		
		if self.selected_reasons:
			lines.append("Why these tasks were selected:")
			for task_id, reason in self.selected_reasons.items():
				lines.append(f"  - {task_id}: {reason}")
		
		if self.unscheduled_reasons:
			lines.append("\nWhy these tasks were not scheduled:")
			for task_id, reason in self.unscheduled_reasons.items():
				lines.append(f"  - {task_id}: {reason}")
		
		return "\n".join(lines) if lines else "No tasks were scheduled today."


class TaskRepository:
	def __init__(self) -> None:
		"""Initialize in-memory task storage keyed by task_id."""
		self._tasks_by_id: dict[str, CareTask] = {}

	def add_task(self, task: CareTask) -> None:
		"""Insert a task by unique task_id, raising ValueError on duplicates."""
		if task.task_id in self._tasks_by_id:
			raise ValueError(f"Task with id {task.task_id} already exists")
		self._tasks_by_id[task.task_id] = task

	def update_task(self, task_id: str, updates: dict[str, Any]) -> None:
		"""Apply partial updates by task_id and keep keys in sync if task_id changes."""
		task = self._tasks_by_id.get(task_id)
		if task is None:
			raise ValueError(f"Task with id {task_id} not found")

		for key, value in updates.items():
			if hasattr(task, key):
				setattr(task, key, value)

		# If task_id itself was updated, keep the dictionary key in sync.
		if task.task_id != task_id:
			if task.task_id in self._tasks_by_id:
				raise ValueError(f"Task with id {task.task_id} already exists")
			self._tasks_by_id.pop(task_id)
			self._tasks_by_id[task.task_id] = task
			return

	def delete_task(self, task_id: str) -> None:
		"""Delete a task by id if it exists, ignoring missing ids."""
		self._tasks_by_id.pop(task_id, None)

	def list_tasks(self) -> list[CareTask]:
		"""Return a shallow list snapshot of all stored tasks."""
		return list(self._tasks_by_id.values())

	def list_tasks_for_pet(self, pet_id: str) -> list[CareTask]:
		"""Return all tasks currently assigned to one pet id."""
		return [t for t in self._tasks_by_id.values() if t.pet_id == pet_id]

	def filter_tasks(
		self,
		pet_id: str | None = None,
		category: TaskCategory | None = None,
		due_date: date | None = None,
	) -> list[CareTask]:
		"""Filter tasks by optional pet, category, and due-date criteria."""
		filtered = list(self._tasks_by_id.values())

		# Apply low-cost filters first, then date-based recurrence checks.
		if pet_id is not None:
			filtered = [t for t in filtered if t.pet_id == pet_id]

		if category is not None:
			filtered = [t for t in filtered if t.category == category]

		if due_date is not None:
			filtered = [t for t in filtered if t.is_due(due_date)]

		return list(filtered)


class Scheduler:
	def detect_time_conflicts(self, items: list[TaskInstance]) -> list[tuple[TaskInstance, TaskInstance]]:
		"""Return pairs of scheduled task instances that overlap in time.

		A conflict is reported whenever two task windows intersect,
		including exact same start times.
		"""
		conflicts: list[tuple[TaskInstance, TaskInstance]] = []
		sorted_items = sorted(items, key=lambda item: (item.scheduled_start, item.scheduled_end))

		for i, left in enumerate(sorted_items):
			for right in sorted_items[i + 1 :]:
				# Since items are start-time sorted, no later items can overlap once this is true.
				if right.scheduled_start >= left.scheduled_end:
					break

				if self._items_overlap(left, right):
					conflicts.append((left, right))

		return conflicts

	def _items_overlap(self, left: TaskInstance, right: TaskInstance) -> bool:
		"""Return whether two scheduled task instances overlap in time."""
		return left.scheduled_start < right.scheduled_end and right.scheduled_start < left.scheduled_end

	def detect_time_conflict_warnings(self, items: list[TaskInstance]) -> list[str]:
		"""Lightweight strategy that reports conflicts as warnings and never raises."""
		warnings: list[str] = []
		valid_items: list[TaskInstance] = []

		try:
			for item in items:
				if not self._has_valid_window(item):
					task_title = getattr(getattr(item, "task", None), "title", "Unknown task")
					warnings.append(
						f"Warning: Skipped conflict check for '{task_title}' because it has an invalid time window."
					)
					continue
				valid_items.append(item)

			for left, right in self.detect_time_conflicts(valid_items):
				left_title = getattr(left.task, "title", "Unknown task")
				right_title = getattr(right.task, "title", "Unknown task")
				left_pet = getattr(left.task, "pet_id", "unknown-pet")
				right_pet = getattr(right.task, "pet_id", "unknown-pet")
				warnings.append(
					f"Warning: '{left_title}' ({left_pet}) conflicts with '{right_title}' ({right_pet}) at "
					f"{left.scheduled_start.strftime('%H:%M')}."
				)
		except Exception as error:
			warnings.append(
				f"Warning: Conflict detection hit an internal issue ({error}) and continued without blocking scheduling."
			)

		return warnings

	def _has_valid_window(self, item: TaskInstance) -> bool:
		"""Return whether a task instance has comparable datetime bounds."""
		start = getattr(item, "scheduled_start", None)
		end = getattr(item, "scheduled_end", None)
		if not isinstance(start, datetime) or not isinstance(end, datetime):
			return False
		return start < end

	def generate_plan(self, tasks: list[CareTask], constraints: DailyConstraints) -> SchedulePlan:
		"""Generate a daily schedule plan from tasks and daily constraints."""
		plan = SchedulePlan(plan_date=constraints.target_date)
		
		# Validate constraints
		if not constraints.validate():
			return plan
		
		# Filter tasks: only those due today and for the active pet.
		due_tasks = self.filter_tasks(tasks, constraints)
		
		# Rank and fit tasks
		ranked = self.rank_tasks(due_tasks, constraints)
		fitted = self.fit_within_budget(ranked, constraints.available_minutes)
		
		# Schedule fitted tasks starting at a reasonable hour (e.g., 8 AM)
		current_time = datetime.combine(constraints.target_date, datetime.min.time().replace(hour=8))
		
		for task in fitted:
			start = current_time
			end = start + timedelta(minutes=task.duration_min)
			instance = TaskInstance(
				task=task,
				scheduled_start=start,
				scheduled_end=end,
				reason="Scheduled based on priority and duration."
			)
			plan.add_item(instance)
			current_time = end
		
		# Identify unscheduled tasks
		fitted_ids = {t.task_id for t in fitted}
		plan.unscheduled_tasks = [t for t in due_tasks if t.task_id not in fitted_ids]
		
		# Build explanation
		explanation = self.build_explanation(plan, due_tasks, constraints)
		plan.explanation = explanation
		plan.warnings.extend(self.detect_time_conflict_warnings(plan.items))
		
		return plan

	def filter_tasks(self, tasks: list[CareTask], constraints: DailyConstraints) -> list[CareTask]:
		"""Filter tasks for the active pet and due date using a deterministic pipeline."""
		filtered = tasks

		if constraints.active_pet_id is not None:
			filtered = [t for t in filtered if t.pet_id == constraints.active_pet_id]

		filtered = [t for t in filtered if t.is_due(constraints.target_date)]
		return filtered

	def rank_tasks(self, tasks: list[CareTask], constraints: DailyConstraints) -> list[CareTask]:
		"""Rank tasks with a stable, deterministic ordering.

		Sort priority:
		1) Earlier time first (task.time when present, otherwise preferred window start)
		2) Narrower preferred windows first
		3) Required tasks before optional tasks
		4) Higher priority score first
		5) Shorter duration first
		6) Title and task_id for deterministic tie-breaking
		"""
		return sorted(tasks, key=lambda task: (self._time_sort_key(task), self._task_sort_key(task)))

	def sort_by_time(self, tasks: list[CareTask]) -> list[CareTask]:
		"""Sort tasks by time, preferring task.time, then preferred_time, then no-time tasks."""
		return sorted(tasks, key=lambda task: (self._time_sort_key(task), task.title.lower(), task.task_id))

	def _time_sort_key(self, task: CareTask) -> tuple[int, int]:
		"""Return a sortable time key for tasks with explicit time or preferred windows."""
		if hasattr(task, "time"):
			time_value = getattr(task, "time")
			if isinstance(time_value, datetime):
				return (0, time_value.hour * 60 + time_value.minute)
			if isinstance(time_value, int):
				return (0, time_value * 60)

		if task.preferred_time is not None:
			return (1, task.preferred_time.start_hour * 60)

		return (2, 24 * 60)

	def _task_sort_key(self, task: CareTask) -> tuple[Any, ...]:
		"""Return a deterministic sort key for a care task."""
		window_span = (
			task.preferred_time.end_hour - task.preferred_time.start_hour
			if task.preferred_time
			else 24
		)
		required_rank = 0 if task.required else 1
		priority_rank = -task.priority

		return (
			window_span,
			required_rank,
			priority_rank,
			task.duration_min,
			task.title.lower(),
			task.task_id,
		)

	def fit_within_budget(self, tasks: list[CareTask], minutes: int) -> list[CareTask]:
		"""Greedily select tasks that fit within the available minute budget."""
		fitted = []
		total_time = 0
		for task in tasks:
			if total_time + task.duration_min <= minutes:
				fitted.append(task)
				total_time += task.duration_min
		return fitted

	def build_explanation(
		self,
		plan: SchedulePlan,
		tasks: list[CareTask],
		constraints: DailyConstraints,
	) -> PlannerExplanation:
		"""Build reasons describing why tasks were scheduled or left unscheduled."""
		explanation = PlannerExplanation()
		
		# Reasons for selected tasks
		scheduled_ids = {item.task.task_id for item in plan.items}
		for item in plan.items:
			explanation.selected_reasons[item.task.task_id] = item.reason
		
		# Reasons for unscheduled tasks
		for task in plan.unscheduled_tasks:
			if plan.total_minutes + task.duration_min > constraints.available_minutes:
				explanation.unscheduled_reasons[task.task_id] = "Not enough time in the schedule."
			else:
				explanation.unscheduled_reasons[task.task_id] = "Lower priority than scheduled tasks."
		
		return explanation


class StreamlitAppController:
	def __init__(self, task_repository: TaskRepository, scheduler: Scheduler) -> None:
		"""Initialize the app controller with a repository and scheduler."""
		self.task_repository = task_repository
		self.scheduler = scheduler

	def collect_owner_pet_info(self) -> Owner:
		"""Collect owner and pet information from the Streamlit UI."""
		# For now, return a stub Owner; will be replaced with Streamlit UI code
		owner = Owner(name="Pet Owner")
		return owner

	def select_active_pet(self, owner: Owner, selected_pet_id: str | None = None) -> Pet | None:
		"""Return the selected pet, auto-selecting when appropriate."""
		if selected_pet_id:
			for pet in owner.pets:
				if pet.pet_id == selected_pet_id:
					return pet
		
		# Auto-select if only one pet
		if len(owner.pets) == 1:
			return owner.pets[0]
		
		# Use default
		return owner.get_default_pet()

	def collect_tasks_input(self) -> list[CareTask]:
		"""Collect task information from the Streamlit UI."""
		return []

	def handle_generate_plan(self, constraints: DailyConstraints) -> tuple[SchedulePlan, PlannerExplanation]:
		"""Generate a plan for the active pet and return it with an explanation."""
		tasks = self.task_repository.list_tasks_for_pet(constraints.active_pet_id or "")
		plan = self.scheduler.generate_plan(tasks, constraints)
		explanation = plan.explanation if hasattr(plan, 'explanation') else PlannerExplanation()
		return plan, explanation

	def display_plan(self, plan: SchedulePlan) -> None:
		"""Display the schedule plan in Streamlit."""
		print(plan.summary())

	def display_explanation(self, explanation: PlannerExplanation) -> None:
		"""Display the planning explanation in Streamlit."""
		print(explanation.render_human_readable())
