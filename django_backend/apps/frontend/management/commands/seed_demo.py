from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import User, Skill, QuizCategory, Question
from apps.companies.models import Company
from apps.jobs.models import Job, JobApplication
from apps.jobs.services.matching_engine import update_application_scores


class Command(BaseCommand):
    help = 'Seeds full demo database with users, companies, jobs, quizzes, and applications.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Starting HireSphere demo data seeding...')

        # 1. Create or update Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hiresphere.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # 2. Create Candidate Job Seekers
        ebin, _ = User.objects.get_or_create(
            username='ebin',
            defaults={
                'email': 'ebin.abraham@hiresphere.edu',
                'first_name': 'Ebin',
                'last_name': 'Abraham',
                'user_type': 'seeker',
                'phone': '+91 94471 23456',
                'headline': 'B.Tech CSE Student | Full Stack & AI Enthusiast',
                'education': 'B.Tech in Computer Science and Engineering, KTU (2022-2026)',
                'experience_years': 1,
                'location': 'Kochi, Kerala',
                'skills': 'Python, Django, SQL, React, REST API, Git, Docker, HTML, CSS',
                'bio': 'Passionate computer science undergraduate focusing on full-stack web architectures, automated ATS resume screening, and machine learning solutions.',
                'resume_score': 85,
                'resume_feedback': (
                    "• Strong ATS compatibility (85%). Essential sections found: Skills, Education, Projects, Experience.\n"
                    "• High technical density across Python, Django, and SQL.\n"
                    "• Tip: Take the Java & Cloud assessment quizzes to expand your verified badges.\n"
                    "• Include link to live deployed projects and portfolio."
                ),
                'is_verified': True,
                'anonymous_in_screening': True,
            }
        )
        ebin.set_password('ebin123')
        ebin.headline = 'B.Tech CSE Student | Full Stack & AI Enthusiast'
        ebin.education = 'B.Tech in Computer Science and Engineering, KTU (2022-2026)'
        ebin.experience_years = 1
        ebin.location = 'Kochi, Kerala'
        ebin.skills = 'Python, Django, SQL, React, REST API, Git, Docker, HTML, CSS'
        ebin.resume_score = 85
        ebin.is_verified = True
        ebin.anonymous_in_screening = True
        ebin.save()

        alex, _ = User.objects.get_or_create(
            username='alex_rivera',
            defaults={
                'email': 'alex.rivera@example.com',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'user_type': 'seeker',
                'phone': '+91 98460 54321',
                'headline': 'Senior Product & UI/UX Designer',
                'education': 'B.Tech in Design and Computing',
                'experience_years': 4,
                'location': 'Bengaluru, India',
                'skills': 'UI/UX Design, Product Strategy, Figma, HTML, CSS, React, Prototyping',
                'resume_score': 88,
                'resume_feedback': '• Well-structured portfolio with verified UX metrics.',
                'is_verified': True,
                'anonymous_in_screening': True,
            }
        )
        alex.set_password('alex123')
        alex.save()

        # 3. Create Verified Skills for Ebin
        verified_skills_data = [
            ('Python', 92, True),
            ('SQL', 88, True),
            ('Web Development', 85, True),
            ('Django', 80, False),
            ('React', 75, False),
            ('REST API', 80, False),
            ('Docker', 65, False),
            ('Git', 85, False),
        ]
        for name, level, is_v in verified_skills_data:
            Skill.objects.update_or_create(
                user=ebin,
                name=name,
                defaults={
                    'level': level,
                    'is_verified': is_v,
                    'verified_at': timezone.now() if is_v else None,
                }
            )

        # 4. Create Companies and Company Recruiter Users
        companies_data = [
            {
                'username': 'tcs_demo',
                'name': 'Tata Consultancy Services (TCS)',
                'website': 'https://www.tcs.com',
                'industry': 'IT Services & Consulting',
                'location': 'Mumbai & Kochi, India',
                'employee_count': '600,000+',
                'description': 'Global leader in IT services, consulting & business solutions partnering with the world’s largest businesses.',
            },
            {
                'username': 'infosys_demo',
                'name': 'Infosys Limited',
                'website': 'https://www.infosys.com',
                'industry': 'Software & IT Consulting',
                'location': 'Bengaluru & Thiruvananthapuram, India',
                'employee_count': '320,000+',
                'description': 'Global leader in next-generation digital services and consulting helping enterprises navigate digital transformation.',
            },
            {
                'username': 'intileo_demo',
                'name': 'Intileo Technologies',
                'website': 'https://www.intileo.com',
                'industry': 'Software Products',
                'location': 'Kochi & Hyderabad, India',
                'employee_count': '500-1000',
                'description': 'Innovative engineering company building cutting-edge enterprise cloud, AI, and web platforms.',
            },
        ]

        company_objects = {}
        for cdata in companies_data:
            c_user, _ = User.objects.get_or_create(
                username=cdata['username'],
                defaults={
                    'email': f"{cdata['username']}@company.com",
                    'first_name': cdata['name'].split()[0],
                    'last_name': 'Recruiter',
                    'user_type': 'company',
                }
            )
            c_user.set_password('demo123')
            c_user.user_type = 'company'
            c_user.save()

            company_obj, _ = Company.objects.update_or_create(
                user=c_user,
                defaults={
                    'name': cdata['name'],
                    'website': cdata['website'],
                    'industry': cdata['industry'],
                    'location': cdata['location'],
                    'employee_count': cdata['employee_count'],
                    'description': cdata['description'],
                    'is_verified': True,
                }
            )
            company_objects[cdata['username']] = company_obj

        # 5. Create Job Openings
        jobs_data = [
            {
                'company': company_objects['tcs_demo'],
                'title': 'Python & Django Backend Developer',
                'description': (
                    'We are seeking a talented Python & Django Developer to build robust backend APIs, '
                    'scalable microservices, and database pipelines for enterprise clients.'
                ),
                'requirements': (
                    '• Proficient with Python 3, Django, and Django REST Framework.\n'
                    '• Solid understanding of relational databases (SQL, PostgreSQL/MySQL).\n'
                    '• Experience designing clean RESTful APIs and unit tests.\n'
                    '• Familiarity with Git, Docker, and CI/CD pipelines.'
                ),
                'skills_required': 'Python, Django, SQL, REST API, Git',
                'salary_min': 500000,
                'salary_max': 850000,
                'job_type': 'full-time',
                'experience_level': '1-3 Years',
                'location': 'Kochi, Kerala / Hybrid',
            },
            {
                'company': company_objects['infosys_demo'],
                'title': 'Full Stack Web Engineer (Python / React)',
                'description': (
                    'Join our modern digital services team engineering responsive, high-performance web applications. '
                    'You will architect both interactive frontend components and resilient backend endpoints.'
                ),
                'requirements': (
                    '• Hands-on experience with Python backend frameworks and React frontend components.\n'
                    '• Proficiency in HTML5, CSS3, JavaScript (ES6+), and responsive layouts.\n'
                    '• Experience working with database models, SQL queries, and ORM.\n'
                    '• Good problem-solving skills and passion for clean code.'
                ),
                'skills_required': 'Python, React, JavaScript, HTML, CSS, SQL',
                'salary_min': 550000,
                'salary_max': 950000,
                'job_type': 'full-time',
                'experience_level': 'Entry - 2 Years',
                'location': 'Bengaluru, India / Remote',
            },
            {
                'company': company_objects['tcs_demo'],
                'title': 'Java Enterprise & Spring Boot Developer',
                'description': (
                    'Looking for strong Core Java developers to design enterprise microservices using Spring Boot, '
                    'Hibernate, and cloud native architectures.'
                ),
                'requirements': (
                    '• Strong command of Java 17+, OOP principles, and Collections.\n'
                    '• Hands-on with Spring Boot, Spring Data JPA, and RESTful web services.\n'
                    '• Good knowledge of SQL databases and transaction management.\n'
                    '• Understanding of microservices communication and message queues.'
                ),
                'skills_required': 'Java, Spring Boot, SQL, MySQL, REST API',
                'salary_min': 600000,
                'salary_max': 1000000,
                'job_type': 'full-time',
                'experience_level': '2-4 Years',
                'location': 'Thiruvananthapuram, Kerala',
            },
            {
                'company': company_objects['intileo_demo'],
                'title': 'Junior Cloud & DevOps Specialist',
                'description': (
                    'Help maintain reliable cloud infrastructure, container orchestration, and continuous integration pipelines.'
                ),
                'requirements': (
                    '• Familiarity with Docker containerization and Dockerfiles.\n'
                    '• Basic knowledge of AWS cloud services (EC2, S3, RDS).\n'
                    '• Scripting abilities in Python or Bash on Linux environments.\n'
                    '• Understanding of Git workflows.'
                ),
                'skills_required': 'Docker, AWS, Linux, Python, Git',
                'salary_min': 450000,
                'salary_max': 750000,
                'job_type': 'full-time',
                'experience_level': 'Entry Level',
                'location': 'Kochi, Kerala',
            },
            {
                'company': company_objects['intileo_demo'],
                'title': 'Database Administrator / SQL Engineer',
                'description': (
                    'Manage high-volume database instances, optimize complex queries, enforce indexing and ensure ACID compliance.'
                ),
                'requirements': (
                    '• Expert in SQL query authoring, window functions, and indexing.\n'
                    '• Experience with PostgreSQL, MySQL, and schema normalization.\n'
                    '• Knowledge of backup, replication, and performance monitoring.'
                ),
                'skills_required': 'SQL, PostgreSQL, MySQL, Database Optimization',
                'salary_min': 650000,
                'salary_max': 1100000,
                'job_type': 'full-time',
                'experience_level': '2-5 Years',
                'location': 'Hyderabad / Remote',
            },
        ]

        created_jobs = []
        for jdata in jobs_data:
            job_obj, _ = Job.objects.update_or_create(
                company=jdata['company'],
                title=jdata['title'],
                defaults={
                    'description': jdata['description'],
                    'requirements': jdata['requirements'],
                    'skills_required': jdata['skills_required'],
                    'salary_min': jdata['salary_min'],
                    'salary_max': jdata['salary_max'],
                    'job_type': jdata['job_type'],
                    'experience_level': jdata['experience_level'],
                    'location': jdata['location'],
                    'is_active': True,
                }
            )
            created_jobs.append(job_obj)

        # 6. Create Quiz Categories and Questions
        quizzes = [
            {
                'name': 'Python',
                'description': 'Validates Python 3 language fundamentals, data structures, generators, decorators, and OOP.',
                'icon': 'fa-brands fa-python',
                'passing_score': 60,
                'questions': [
                    {
                        'question': 'Which of the following data structures in Python is mutable?',
                        'option1': 'Tuple',
                        'option2': 'List',
                        'option3': 'String',
                        'option4': 'Frozenset',
                        'correct_answer': 'List',
                        'explanation': 'Lists in Python are mutable, meaning their elements can be modified in place. Tuples, strings, and frozensets are immutable.',
                    },
                    {
                        'question': 'What does the *args parameter in a Python function definition allow you to do?',
                        'option1': 'Pass keyword arguments as a dictionary',
                        'option2': 'Pass an arbitrary number of positional arguments as a tuple',
                        'option3': 'Enforce strictly typed arguments',
                        'option4': 'Call the function in a separate thread',
                        'correct_answer': 'Pass an arbitrary number of positional arguments as a tuple',
                        'explanation': '*args gathers extra positional arguments into a tuple, while **kwargs gathers keyword arguments into a dictionary.',
                    },
                    {
                        'question': 'In Python, what is the time complexity of searching for a key in a standard dictionary (average case)?',
                        'option1': 'O(1)',
                        'option2': 'O(n)',
                        'option3': 'O(log n)',
                        'option4': 'O(n log n)',
                        'correct_answer': 'O(1)',
                        'explanation': 'Python dictionaries use hash tables under the hood, yielding O(1) average-case time complexity for lookups, insertions, and deletions.',
                    },
                    {
                        'question': 'What is the purpose of the __init__ method in a Python class?',
                        'option1': 'It destroys the class instance from memory',
                        'option2': 'It acts as the constructor to initialize new object attributes',
                        'option3': 'It imports external modules into the class scope',
                        'option4': 'It converts the object to a string representation',
                        'correct_answer': 'It acts as the constructor to initialize new object attributes',
                        'explanation': '__init__ is the initializer method automatically called when a new instance of the class is created.',
                    },
                    {
                        'question': 'Which Python keyword is used to create a generator function?',
                        'option1': 'return',
                        'option2': 'yield',
                        'option3': 'generate',
                        'option4': 'await',
                        'correct_answer': 'yield',
                        'explanation': 'The yield keyword transforms a function into a generator that produces values one at a time on demand without storing everything in memory.',
                    },
                ],
            },
            {
                'name': 'Java',
                'description': 'Validates Core Java, OOP inheritance, JVM architecture, exceptions, and Collections framework.',
                'icon': 'fa-brands fa-java',
                'passing_score': 60,
                'questions': [
                    {
                        'question': 'Which Java feature prevents a class from being inherited/subclassed?',
                        'option1': 'abstract',
                        'option2': 'static',
                        'option3': 'final',
                        'option4': 'volatile',
                        'correct_answer': 'final',
                        'explanation': 'Declaring a class as final in Java prevents any other class from extending it.',
                    },
                    {
                        'question': 'Which Collection interface in Java does NOT allow duplicate elements?',
                        'option1': 'List',
                        'option2': 'Set',
                        'option3': 'Queue',
                        'option4': 'ArrayList',
                        'correct_answer': 'Set',
                        'explanation': 'The Set interface represents a collection of unique elements and models the mathematical set abstraction.',
                    },
                    {
                        'question': 'Where are Java object instances stored in memory during runtime?',
                        'option1': 'Stack Memory',
                        'option2': 'Heap Memory',
                        'option3': 'Register',
                        'option4': 'Class Loader',
                        'correct_answer': 'Heap Memory',
                        'explanation': 'All Java objects and instance variables are allocated on the Heap memory, managed by the Garbage Collector.',
                    },
                    {
                        'question': 'Which keyword is used to explicitly throw an exception in Java?',
                        'option1': 'throws',
                        'option2': 'throw',
                        'option3': 'catch',
                        'option4': 'try',
                        'correct_answer': 'throw',
                        'explanation': '"throw" is used to explicitly throw an exception instance, whereas "throws" declares exceptions that a method might raise.',
                    },
                    {
                        'question': 'In Java, multiple inheritance of classes is achieved using which concept?',
                        'option1': 'Abstract Classes',
                        'option2': 'Interfaces',
                        'option3': 'Inner Classes',
                        'option4': 'Packages',
                        'correct_answer': 'Interfaces',
                        'explanation': 'Java does not support multiple inheritance with classes to avoid ambiguity (Diamond problem), but supports it through interfaces.',
                    },
                ],
            },
            {
                'name': 'Web Development',
                'description': 'Assesses full-stack web standards: HTML5 semantic tags, CSS layout, JavaScript async, and REST APIs.',
                'icon': 'fa-code',
                'passing_score': 60,
                'questions': [
                    {
                        'question': 'Which HTTP method is idempotent and designed to update/replace an entire resource in REST APIs?',
                        'option1': 'POST',
                        'option2': 'PUT',
                        'option3': 'PATCH',
                        'option4': 'CONNECT',
                        'correct_answer': 'PUT',
                        'explanation': 'PUT is idempotent and replaces the entire target resource with the uploaded payload.',
                    },
                    {
                        'question': 'In CSS Flexbox, which property aligns items along the cross axis?',
                        'option1': 'justify-content',
                        'option2': 'align-items',
                        'option3': 'flex-direction',
                        'option4': 'flex-wrap',
                        'correct_answer': 'align-items',
                        'explanation': 'align-items controls alignment on the cross axis, whereas justify-content aligns along the main axis.',
                    },
                    {
                        'question': 'What does the HTTP 403 Forbidden status code indicate?',
                        'option1': 'The requested page was not found on the server',
                        'option2': 'The server understood the request but refuses to authorize it',
                        'option3': 'The client has not provided authentication credentials',
                        'option4': 'The server encountered an unexpected internal error',
                        'correct_answer': 'The server understood the request but refuses to authorize it',
                        'explanation': '403 Forbidden means the server recognized the client identity but permissions/roles are insufficient.',
                    },
                    {
                        'question': 'Which keyword in JavaScript handles asynchronous promises inside an async function?',
                        'option1': 'defer',
                        'option2': 'await',
                        'option3': 'then',
                        'option4': 'resolve',
                        'correct_answer': 'await',
                        'explanation': '"await" pauses async function execution until the Promise resolves or rejects, returning the resolved value.',
                    },
                    {
                        'question': 'What is the role of CSRF (Cross-Site Request Forgery) protection tokens in web forms?',
                        'option1': 'To encrypt the user passwords before sending them to the database',
                        'option2': 'To verify that the form submission originated from the authentic user on the current site',
                        'option3': 'To compress the HTTP payload size for faster transmission',
                        'option4': 'To store browser cookies permanently',
                        'correct_answer': 'To verify that the form submission originated from the authentic user on the current site',
                        'explanation': 'CSRF tokens ensure that state-changing POST/PUT requests cannot be hijacked by malicious third-party websites.',
                    },
                ],
            },
            {
                'name': 'SQL',
                'description': 'Tests database queries, joins, aggregate functions, indexing, and normalization rules.',
                'icon': 'fa-database',
                'passing_score': 60,
                'questions': [
                    {
                        'question': 'Which SQL clause is used to filter records after applying an aggregate GROUP BY function?',
                        'option1': 'WHERE',
                        'option2': 'HAVING',
                        'option3': 'ORDER BY',
                        'option4': 'FILTER',
                        'correct_answer': 'HAVING',
                        'explanation': 'WHERE filters rows before aggregation; HAVING filters groups after aggregation.',
                    },
                    {
                        'question': 'What type of JOIN returns all records from the left table and matched records from the right table?',
                        'option1': 'INNER JOIN',
                        'option2': 'LEFT JOIN',
                        'option3': 'FULL OUTER JOIN',
                        'option4': 'CROSS JOIN',
                        'correct_answer': 'LEFT JOIN',
                        'explanation': 'A LEFT JOIN returns all rows from the left table, with NULLs for unmatched rows from the right table.',
                    },
                    {
                        'question': 'What does the "A" in ACID database properties stand for?',
                        'option1': 'Accuracy',
                        'option2': 'Atomicity',
                        'option3': 'Availability',
                        'option4': 'Authentication',
                        'correct_answer': 'Atomicity',
                        'explanation': 'Atomicity guarantees that all operations within a transaction succeed completely or none take effect.',
                    },
                    {
                        'question': 'A database table is in Third Normal Form (3NF) if it is in 2NF and has no:',
                        'option1': 'Primary keys',
                        'option2': 'Transitive dependencies',
                        'option3': 'Foreign keys',
                        'option4': 'Repeating groups',
                        'correct_answer': 'Transitive dependencies',
                        'explanation': '3NF requires that no non-prime attribute is transitively dependent on the primary key.',
                    },
                    {
                        'question': 'What is the primary benefit of creating an index on a frequently searched column in SQL?',
                        'option1': 'Reduces the physical disk space used by the database',
                        'option2': 'Accelerates data retrieval speeds for SELECT queries with WHERE filters',
                        'option3': 'Guarantees automatic data backup on every insert',
                        'option4': 'Enforces password encryption on the table',
                        'correct_answer': 'Accelerates data retrieval speeds for SELECT queries with WHERE filters',
                        'explanation': 'Indexes create B-tree structures that allow the database engine to locate records without full table scans.',
                    },
                ],
            },
        ]

        for qdata in quizzes:
            cat_obj, _ = QuizCategory.objects.update_or_create(
                name=qdata['name'],
                defaults={
                    'description': qdata['description'],
                    'icon': qdata['icon'],
                    'passing_score': qdata['passing_score'],
                }
            )
            # Remove old questions to avoid duplicate accumulation
            cat_obj.questions.all().delete()
            for qitem in qdata['questions']:
                Question.objects.create(
                    category=cat_obj,
                    question=qitem['question'],
                    option1=qitem['option1'],
                    option2=qitem['option2'],
                    option3=qitem['option3'],
                    option4=qitem['option4'],
                    correct_answer=qitem['correct_answer'],
                    explanation=qitem['explanation'],
                )

        # 7. Create Sample Job Applications for Demonstration
        # Application 1: Ebin to Python/Django Developer at TCS
        app1, _ = JobApplication.objects.update_or_create(
            job=created_jobs[0],
            applicant=ebin,
            defaults={
                'cover_letter': 'I have built multiple Python and Django web applications with full database integration and verified skill competencies.',
                'status': 'shortlisted',
            }
        )
        update_application_scores(app1)

        # Application 2: Ebin to Full Stack Web Engineer at Infosys
        app2, _ = JobApplication.objects.update_or_create(
            job=created_jobs[1],
            applicant=ebin,
            defaults={
                'cover_letter': 'Excited to contribute to modern full stack engineering with verified Python and web development badges.',
                'status': 'pending',
            }
        )
        update_application_scores(app2)

        self.stdout.write(self.style.SUCCESS('Successfully seeded HireSphere database!'))
        self.stdout.write(self.style.SUCCESS(f'Created: 1 Admin, 2 Candidates, 3 Companies, {len(created_jobs)} Jobs, {len(quizzes)} Skill Quizzes.'))
