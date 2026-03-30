import streamlit as st
from datetime import date
import uuid

from pawpals_system import (
    CareTask,
    DailyConstraints,
    Frequency,
    Owner,
    Pet,
    Scheduler,
    TaskCategory,
    TaskRepository,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

# Keep one Owner instance in session state across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
else:
    st.session_state.owner.name = owner_name

if "task_repository" not in st.session_state:
    st.session_state.task_repository = TaskRepository()

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

st.markdown("### Add Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age_years = st.number_input("Age (years)", min_value=0, max_value=40, value=2)
    weight_kg = st.number_input("Weight (kg)", min_value=0.1, max_value=120.0, value=6.0)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    new_pet = Pet(
        pet_id=str(uuid.uuid4()),
        name=pet_name,
        species=species,
        age_years=int(age_years),
        weight_kg=float(weight_kg),
    )
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added pet: {new_pet.name}")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "age_years": pet.age_years,
                "weight_kg": pet.weight_kg,
            }
            for pet in st.session_state.owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    category_label = st.selectbox(
        "Category",
        [c.value for c in TaskCategory],
        index=0,
    )

active_pet_options = {
    f"{pet.name} ({pet.species})": pet.pet_id for pet in st.session_state.owner.pets
}
selected_pet_label = st.selectbox(
    "Assign task to pet",
    list(active_pet_options.keys()),
    disabled=not bool(active_pet_options),
)

if st.button("Add task"):
    if not active_pet_options:
        st.error("Add a pet before adding tasks.")
    else:
        priority_map = {"low": 1, "medium": 2, "high": 3}
        new_task = CareTask(
            task_id=str(uuid.uuid4()),
            pet_id=active_pet_options[selected_pet_label],
            title=task_title,
            category=TaskCategory(category_label),
            duration_min=int(duration),
            priority=priority_map[priority_label],
            frequency=Frequency.DAILY,
        )
        st.session_state.task_repository.add_task(new_task)
        st.success(f"Added task: {new_task.title}")

all_tasks = st.session_state.task_repository.list_tasks()
if all_tasks:
    st.write("Current tasks")

    selected_pet_id = active_pet_options.get(selected_pet_label) if active_pet_options else None
    preview_constraints = DailyConstraints(
        target_date=date.today(),
        available_minutes=24 * 60,
        max_tasks=999,
        active_pet_id=selected_pet_id,
    )
    filtered_tasks = st.session_state.scheduler.filter_tasks(all_tasks, preview_constraints)
    sorted_filtered_tasks = st.session_state.scheduler.sort_by_time(filtered_tasks)

    if sorted_filtered_tasks:
        st.success(
            f"Showing {len(sorted_filtered_tasks)} due tasks for the selected pet, sorted by scheduler time rules."
        )
        st.table(
            [
                {
                    "title": task.title,
                    "category": task.category.value,
                    "duration_minutes": task.duration_min,
                    "priority": task.priority,
                    "required": task.required,
                    "preferred_window": (
                        f"{task.preferred_time.start_hour:02d}:00-{task.preferred_time.end_hour:02d}:00"
                        if task.preferred_time
                        else "anytime"
                    ),
                }
                for task in sorted_filtered_tasks
            ]
        )
    else:
        st.warning("No due tasks match the selected pet/date filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This now calls your scheduler and displays a generated plan.")

available_minutes = st.number_input(
    "Available minutes today",
    min_value=1,
    max_value=720,
    value=120,
)
max_tasks = st.number_input(
    "Max tasks to schedule",
    min_value=1,
    max_value=20,
    value=5,
)

if st.button("Generate schedule"):
    if not active_pet_options:
        st.error("Add a pet first.")
    else:
        active_pet_id = active_pet_options[selected_pet_label]
        constraints = DailyConstraints(
            target_date=date.today(),
            available_minutes=int(available_minutes),
            max_tasks=int(max_tasks),
            active_pet_id=active_pet_id,
        )
        pet_tasks = st.session_state.task_repository.list_tasks_for_pet(active_pet_id)
        plan = st.session_state.scheduler.generate_plan(pet_tasks, constraints)

        if not plan.items:
            st.info("No tasks could be scheduled with the current constraints.")
        else:
            st.success(
                f"Scheduled {len(plan.items)} task(s) totaling {plan.total_minutes} minutes for today."
            )
            st.write("Generated plan")
            st.table(
                [
                    {
                        "task": item.task.title,
                        "pet_id": item.task.pet_id,
                        "start": item.scheduled_start.strftime("%H:%M"),
                        "end": item.scheduled_end.strftime("%H:%M"),
                        "reason": item.reason,
                    }
                    for item in plan.items
                ]
            )
            st.caption(plan.summary())

        if plan.warnings:
            st.warning(
                "Potential schedule conflicts were detected. Review the overlapping items below before relying on this plan."
            )
            for warning in plan.warnings:
                st.warning(warning)
            st.info(
                "Helpful tip: if two tasks overlap, move one to a later time window or reduce today's max tasks."
            )

        if plan.unscheduled_tasks:
            st.write("Unscheduled tasks:")
            st.table(
                [
                    {
                        "task": task.title,
                        "duration_minutes": task.duration_min,
                        "priority": task.priority,
                    }
                    for task in plan.unscheduled_tasks
                ]
            )
