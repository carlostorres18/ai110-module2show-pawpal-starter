from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


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


class TaskStatus(Enum):
	PLANNED = "planned"
	DONE = "done"
	SKIPPED = "skipped"


@dataclass
class TimeWindow:
	start_hour: int
	end_hour: int

	def contains(self, hour: int) -> bool:
		pass


@dataclass
class Owner:
	name: str
	preferences: dict[str, Any] = field(default_factory=dict)
	available_minutes_per_day: int = 0

	def add_preference(self, key: str, value: Any) -> None:
		pass

	def get_preference(self, key: str) -> Any:
		pass


@dataclass
class Pet:
	name: str
	species: str
	age_years: int
	weight_kg: float
	notes: str = ""


@dataclass
class CareTask:
	task_id: str
	title: str
	category: TaskCategory
	duration_min: int
	priority: int
	frequency: Frequency
	required: bool = False
	preferred_time: TimeWindow | None = None
	notes: str = ""

	def is_due(self, target_date: date) -> bool:
		pass

	def score(self, constraints: DailyConstraints) -> float:
		pass


@dataclass
class DailyConstraints:
	target_date: date
	available_minutes: int
	max_tasks: int
	blocked_windows: list[TimeWindow] = field(default_factory=list)
	energy_level: int = 5

	def validate(self) -> bool:
		pass


@dataclass
class TaskInstance:
	task: CareTask
	scheduled_start: datetime
	scheduled_end: datetime
	reason: str
	status: TaskStatus = TaskStatus.PLANNED

	def mark_done(self) -> None:
		pass

	def mark_skipped(self) -> None:
		pass


@dataclass
class SchedulePlan:
	plan_date: date
	items: list[TaskInstance] = field(default_factory=list)
	total_minutes: int = 0
	unscheduled_tasks: list[CareTask] = field(default_factory=list)

	def add_item(self, item: TaskInstance) -> None:
		pass

	def remove_item(self, task_id: str) -> None:
		pass

	def summary(self) -> str:
		pass


@dataclass
class PlannerExplanation:
	selected_reasons: dict[str, str] = field(default_factory=dict)
	unscheduled_reasons: dict[str, str] = field(default_factory=dict)

	def render_human_readable(self) -> str:
		pass


class TaskRepository:
	def __init__(self) -> None:
		self.tasks: list[CareTask] = []

	def add_task(self, task: CareTask) -> None:
		pass

	def update_task(self, task_id: str, updates: dict[str, Any]) -> None:
		pass

	def delete_task(self, task_id: str) -> None:
		pass

	def list_tasks(self) -> list[CareTask]:
		pass


class Scheduler:
	def generate_plan(self, tasks: list[CareTask], constraints: DailyConstraints) -> SchedulePlan:
		pass

	def rank_tasks(self, tasks: list[CareTask], constraints: DailyConstraints) -> list[CareTask]:
		pass

	def fit_within_budget(self, tasks: list[CareTask], minutes: int) -> list[CareTask]:
		pass

	def build_explanation(
		self,
		plan: SchedulePlan,
		tasks: list[CareTask],
		constraints: DailyConstraints,
	) -> PlannerExplanation:
		pass


class StreamlitAppController:
	def __init__(self, task_repository: TaskRepository, scheduler: Scheduler) -> None:
		self.task_repository = task_repository
		self.scheduler = scheduler

	def collect_owner_pet_info(self) -> tuple[Owner, Pet]:
		pass

	def collect_tasks_input(self) -> list[CareTask]:
		pass

	def handle_generate_plan(self, constraints: DailyConstraints) -> tuple[SchedulePlan, PlannerExplanation]:
		pass

	def display_plan(self, plan: SchedulePlan) -> None:
		pass

	def display_explanation(self, explanation: PlannerExplanation) -> None:
		pass
