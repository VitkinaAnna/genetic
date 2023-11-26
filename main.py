TEACHER_OVERWORKED_PENALTY = 1
TEACHER_SPLIT_PENALTY = 1
GROUP_SPLIT_PENALTY = 1
MUTATION_RATIO = 0.001
NUM_GENERATION = 1000
POPULATION = 200
TIME_SLOTS = 20

class Group:
    def __init__(self, _id, _name, _courses):
        self.id = _id
        self.name = _name
        self.courses = _courses

class Course:
    def __init__(self, _id, _name, _lecture_hours, _lab_hours, _qualified_teachers):
        self.id = _id
        self.name = _name
        self.lecture_hours = _lecture_hours
        self.lab_hours = _lab_hours
        self.qualified_teachers = _qualified_teachers

class Teacher:
    def __init__(self, _id, _name, _max_hours):
        self.id = _id
        self.name = _name
        self.max_hours = _max_hours

class Meeting:
    def __init__(self, _teacher_id, _group_id, _course_id, _is_lecture, _meeting_time):
        self.teacher_id = _teacher_id
        self.group_id = _group_id
        self.course_id = _course_id
        self.is_lecture = _is_lecture
        self.meeting_time = _meeting_time

class Data:
    def __init__(self):
        self.teachers = [
            Teacher(0, "Бобиль Б.В.", 20),
            Teacher(1, "Тарануха В.Ю.", 20),
            Teacher(2, "Федорус О.М.", 20),
            Teacher(3, "Вергунова І.М.", 20),
            Teacher(4, "Ткаченко О.М.", 20),
            Teacher(5, "Терещенко Я.В.", 20),
            Teacher(6, "Криволап А.В.", 20),
            Teacher(7, "Волошин О.Ф.", 20),
            Teacher(8, "Пашко А.О.", 20),
            Teacher(9, "Глибовець М.М.", 20)
        ]

        course1 = Course(1, "Інтелектуальні системи", 1, 1, [self.teachers[2], self.teachers[1], self.teachers[9]])
        course2 = Course(2, "Нейронні мережі та основи комп лінгвістики", 3, 2, [self.teachers[0], self.teachers[1]])
        course3 = Course(3, "Основи комп алгоритмів", 0, 2, [self.teachers[1]])
        course4 = Course(4, "Складність алгоритмів", 2, 0, [self.teachers[3]])
        course5 = Course(5, "Інформаційні технології", 2, 1, [self.teachers[5], self.teachers[6], self.teachers[4]])
        course6 = Course(6, "Теорія прийняття рішень", 1, 1, [self.teachers[7]])
        course7 = Course(7, "Статистичне моделювання", 1, 0, [self.teachers[8]])

        self.courses = [course1, course2, course3, course4, course5, course6, course7]

        group1_courses = [course1, course2, course3, course4]
        group1 = Group(1, "МІ-4", group1_courses)

        group2_courses = [course2, course3, course4, course5]
        group2 = Group(2, "ТК-4", group2_courses)

        group3_courses = [course3, course4, course5, course6]
        group3 = Group(3, "ТТП-4", group3_courses)

        group4_courses = [course4, course5, course6, course7]
        group4 = Group(4, "СА-4", group4_courses)

        self.groups = [group1, group2, group3, group4]


class Schedule:
    def __init__(self, data=None):
        self.meetings = []
        self.fitness_value = 0
        self.num_classes = 0
        self.num_conflicts = 0

        if data:
            self.generate_schedule(data)

    def generate_schedule(self, data):
        self.fitness_value = 0
        self.num_classes = 0
        self.num_conflicts = 0

        for group in data.groups:
            for course in group.courses:
                # Додати декції
                for _ in range(course.lecture_hours):
                    selected_teacher = random.choice(course.qualified_teachers)
                    random_meeting_time = random.randint(0, TIME_SLOTS - 1)
                    meeting = Meeting(selected_teacher.id, group.id, course.id, True, random_meeting_time)
                    self.meetings.append(meeting)
                    self.num_classes += 1

                # Додати лаборатоні
                for _ in range(course.lab_hours):
                    selected_teacher = random.choice(course.qualified_teachers)
                    random_meeting_time = random.randint(0, TIME_SLOTS - 1)
                    meeting = Meeting(selected_teacher.id, group.id, course.id, False, random_meeting_time)
                    self.meetings.append(meeting)
                    self.num_classes += 1

    def calculate_fitness(self, data):
        conflicts = self.calculate_conflicts(data)
        self.fitness_value = 1 / (1 + conflicts)
        return self.fitness_value

    def calculate_conflicts(self, data):
        self.num_conflicts = 0

        group_slots = {}
        teacher_teaching_hours = {}

        for meeting in self.meetings:
            if meeting.group_id not in group_slots:
                group_slots[meeting.group_id] = set()

            if meeting.meeting_time in group_slots[meeting.group_id]:
                self.num_conflicts += GROUP_SPLIT_PENALTY
            else:
                group_slots[meeting.group_id].add(meeting.meeting_time)

        teacher_slots = {}

        for meeting in self.meetings:
            teacher_teaching_hours[meeting.teacher_id] = teacher_teaching_hours.get(meeting.teacher_id, 0) + 1

            if meeting.teacher_id not in teacher_slots:
                teacher_slots[meeting.teacher_id] = set()

            if meeting.is_lecture:
                is_same_subject_lecture = any(
                    subject_id == meeting.course_id and time == meeting.meeting_time and is_lecture == meeting.is_lecture
                    for subject_id, time, is_lecture in teacher_slots[meeting.teacher_id]
                )

                if is_same_subject_lecture:
                    teacher_teaching_hours[meeting.teacher_id] -= 1
                elif not is_same_subject_lecture:
                    teacher_slots[meeting.teacher_id].add((meeting.course_id, meeting.meeting_time, meeting.is_lecture))
            else:
                is_same_subject_lab = any(
                    subject_id == meeting.course_id and time == meeting.meeting_time
                    for subject_id, time, _ in teacher_slots[meeting.teacher_id]
                )

                if is_same_subject_lab:
                    self.num_conflicts += TEACHER_SPLIT_PENALTY
                else:
                    teacher_slots[meeting.teacher_id].add((meeting.course_id, meeting.meeting_time, meeting.is_lecture))

        for teacher_id, teaching_hours in teacher_teaching_hours.items():
            if teaching_hours > data.teachers[teacher_id].max_hours:
                self.num_conflicts += (teaching_hours - data.teachers[teacher_id].max_hours) * TEACHER_OVERWORKED_PENALTY

        return self.num_conflicts

    def print_schedule(self):
        for meeting in self.meetings:
            print(
                f"Teacher ID: {meeting.teacher_id}, Group ID: {meeting.group_id}, Course ID: {meeting.course_id}, "
                f"Is Lecture: {'Yes' if meeting.is_lecture else 'No'}, Meeting Time: {meeting.meeting_time}"
            )

    def copy_schedule(self):
        new_schedule = Schedule()
        new_schedule.meetings = [Meeting(m.teacher_id, m.group_id, m.course_id, m.is_lecture, m.meeting_time) for m in
                                 self.meetings]
        new_schedule.fitness_value = self.fitness_value
        new_schedule.num_classes = self.num_classes
        new_schedule.num_conflicts = self.num_conflicts
        return new_schedule

class Population:
    def __init__(self, size, data=None):
        self.size = size
        self.schedules = []

        if data is not None:
            self.initialize_schedules(data)

    def initialize_schedules(self, data):
        for _ in range(self.size):
            schedule = Schedule(data)
            self.schedules.append(schedule)

import random

class GeneticAlgorithm:

    ELITISM_NUM = 5

    def crossover_schedule(self, schedule1, schedule2):
        new_schedule = schedule1.copy_schedule()

        for i in range(len(schedule1.meetings)):
            if random.choice([True, False]):
                new_schedule.meetings[i] = schedule1.meetings[i]
            else:
                new_schedule.meetings[i] = schedule2.meetings[i]

        return new_schedule

    def mutate_schedule(self, schedule, data):
        result_schedule = Schedule(data)
        temp_schedule = Schedule(data)

        for i in range(len(schedule.meetings)):
            if random.random() < MUTATION_RATIO:
                result_schedule.meetings[i] = temp_schedule.meetings[i]
            else:
                result_schedule.meetings[i] = schedule.meetings[i]

        return result_schedule

    def mutate_population(self, population, data):
        for i in range(len(population.schedules)):
            population.schedules[i] = self.mutate_schedule(population.schedules[i], data)

    def crossover_population(self, population):
        new_population = Population(size=POPULATION)

        sorted_schedules = sorted(population.schedules, key=lambda x: x.fitness_value, reverse=True)

        # Обрати найкращий розклад
        new_population.schedules.extend(sorted_schedules[:self.ELITISM_NUM])

        while len(new_population.schedules) < POPULATION:
            index1 = random.randint(0, len(sorted_schedules) - 1)
            index2 = random.randint(0, len(sorted_schedules) - 1)

            child_schedule = self.crossover_schedule(sorted_schedules[index1], sorted_schedules[index2])
            new_population.schedules.append(child_schedule)

        return new_population

def main():
    data = Data()

    population = Population(POPULATION, data)

    genetic_algo = GeneticAlgorithm()

    for generation in range(NUM_GENERATION):
        for schedule in population.schedules:
            schedule.calculate_fitness(data)

        best_schedule = max(population.schedules, key=lambda x: x.fitness_value)
        worst_schedule = min(population.schedules, key=lambda x: x.fitness_value)

        if best_schedule.fitness_value == 1 or generation == NUM_GENERATION - 1:
            print("Generation:", generation)
            print("Best Fitness:", best_schedule.fitness_value)
            print("Worst Fitness:", worst_schedule.fitness_value)
            print("Number of Classes:", best_schedule.num_classes)
            print("Number of Conflicts:", best_schedule.num_conflicts)

            print("Meetings of the Best Schedule:")
            best_schedule.print_schedule()

            print("--------------------------------------")
            return 0

        if generation % 10 == 0:
            print("Generation:", generation)

            best_schedule = max(population.schedules, key=lambda x: x.fitness_value)
            worst_schedule = min(population.schedules, key=lambda x: x.fitness_value)

            print("Best Fitness:", best_schedule.fitness_value)
            print("Worst Fitness:", worst_schedule.fitness_value)
            print("Number of Classes:", best_schedule.num_classes)
            print("Number of Conflicts:", best_schedule.num_conflicts)

            print("--------------------------------------")

        new_population = genetic_algo.crossover_population(population)

        genetic_algo.mutate_population(new_population, data)

        population = new_population

    return 0

if __name__ == "__main__":
    main()
