# Criteria A – Planning

## Defining the Problem

This project addresses a real need identified through an interview with Sarah, a mother of middle school students. She requires a simple and reliable way for her children to practise school subjects at home without depending on commercial online platforms or continuous internet access. At present, her children do not have a focused, structured tool on the family laptop that allows them to practise key topics such as Physics, Chemistry, and Mathematics in short, purposeful sessions. Existing web-based solutions are often distracting, include advertisements, require user accounts, or involve complex configuration that is not appropriate for a typical home environment.

From the interview, Sarah’s essential requirements can be summarised as follows:
- The application must run **locally on her laptop**, with **no internet connection required** once installed.
- Before beginning a session, her children must be able to select a **subject** (Physics, Chemistry, or Math) and a **difficulty level** (Easy, Medium, or Hard).
- Each practice session should contain **10 questions by default**, providing a short, manageable assessment that can fit into their daily routine.
- All questions should be **multiple choice with four options**, to simplify input, avoid spelling errors, and enable automatic marking.
- At the end of each session, the application must display the **overall score** and a **review section** listing the questions answered incorrectly together with the correct answers.

The problem can therefore be defined as the need for a small, standalone practice application that allows a parent to maintain a bank of questions and enables children to complete targeted, 10-question multiple-choice sessions with immediate feedback and a structured review of mistakes, all on a single laptop without complex installation or configuration.

As a high school student and the developer of this system, I discussed both the problem context and the proposed solution with my IB Computer Science teacher. I presented Sarah’s requirements, the constraint that the solution must run offline, the use of a CSV-based question bank, and the plan for fixed-length sessions with a detailed results page. My teacher confirmed that the problem is clearly defined, appropriately scoped for an IB Computer Science SL project, and technically feasible using the tools and concepts covered in the course. On this basis, the problem statement and proposed direction have been validated and I will proceed with implementation.

## Rationale for the Proposed Solution

The proposed solution is implemented using **Python**, **HTML with htmx**, **CSS**, and **Jinja2 templates**, with a **CSV file** serving as the underlying data store for the question bank. This technology stack has been selected to balance technical rigour, simplicity of deployment, and alignment with the project constraints.

Python is an appropriate choice for the core application logic because it is the main programming language used in my Computer Science course and provides strong standard-library support for **file input/output** and **CSV processing**. These features directly support the requirement to load questions from a simple text-based file. Python also enables the use of key programming constructs expected in IB Computer Science, such as collections (lists) for storing questions and responses, user-defined classes for entities like questions and sessions, selection and iteration structures, and robust error handling. This makes the code both educationally meaningful and maintainable.

On the front end, I will use HTML enhanced with **htmx**. htmx allows the browser to request and update specific parts of a web page from the Python backend without requiring a full single-page application framework. This approach provides a responsive user experience for interactions such as loading the next question or submitting an answer, while keeping the architecture comparatively simple. **CSS** will be used to design a clear, uncluttered interface so that middle school students can focus on the learning tasks rather than the interface itself.

The presentation layer will be generated using **Jinja2** templates. Jinja2 integrates effectively with Python-based web frameworks and supports the dynamic generation of pages for topic and difficulty selection, question presentation, and results reporting. Using templates enforces a separation between presentation and business logic, which improves readability and makes future extensions (for example, adding new subjects or alternative views of results) easier to implement.

Finally, the project deliberately uses a **CSV file instead of a database management system**. A CSV file can be created and edited using common tools such as spreadsheet applications, enabling Sarah to update or extend the question bank without specialised technical knowledge. Avoiding a separate database server keeps the application **standalone** and reduces installation complexity: there is no need to configure additional services, user accounts, or network connectivity. This design decision directly supports the original requirement for a simple, easy-to-maintain practice application that can run entirely on a home laptop, independently of the internet.
