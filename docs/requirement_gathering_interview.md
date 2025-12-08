# Requirements Gathering Interview

**Project**: Q&A Practice Application  
**Date**: 2025-12-02  
**Interviewer**: Software Developer (Dev)  
**Interviewee**: Sarah (Mother of middle school student)  
**Duration**: ~45 minutes

---

## Interview Transcript

### Opening

**Dev**: Hi Sarah, thank you for taking the time to meet with me today. I understand you're looking for an application to help your kids practice their schoolwork. Can you tell me a bit about what you have in mind?

**Sarah**: Hi! Yes, absolutely. My kids are in middle school and I've been looking for a simple way for them to practice their subjects at home. Nothing fancy—just something that can run on my laptop where they can answer some questions and see how they did.

---

### Understanding the Core Need

**Dev**: That sounds like a great idea. Let's start with the basics. What subjects are your kids studying that you'd like them to practice?

**Sarah**: Right now, the main ones would be Physics, Chemistry, and Math. Those are the subjects they need the most help with.

**Dev**: Got it. So we're looking at three subjects: Physics, Chemistry, and Math. Are there any other subjects you might want to add later?

**Sarah**: Maybe, but let's start with those three. If it works well, we can always add more later, right?

**Dev**: Absolutely, we can design it to be expandable. Now, within each subject, do your kids study different levels of difficulty? Like beginner topics versus more advanced ones?

**Sarah**: Oh yes! That's actually really important. Some topics they've mastered, and others they're still struggling with. It would be great if they could choose how hard the questions are.

**Dev**: How would you like to categorize the difficulty? Would something like Easy, Medium, and Hard work?

**Sarah**: Yes, that's perfect. Three levels should be enough. Easy for when they're just starting a topic, Medium for regular practice, and Hard for when they want a challenge.

---

### Question Format and Session Structure

**Dev**: Let's talk about the questions themselves. What format are you thinking? Open-ended questions where they type an answer, or multiple choice?

**Sarah**: Multiple choice would be better, I think. It's easier for the kids to use, and honestly, it's easier for me to set up. I don't want them getting frustrated typing answers and getting marked wrong because of a spelling mistake.

**Dev**: That makes sense. How many answer options would you like for each question?

**Sarah**: Four options seems standard, right? Like what they see on their school tests.

**Dev**: Four options it is. Now, how many questions should they answer in one sitting? Do you want them to go through all available questions, or would you prefer shorter practice sessions?

**Sarah**: Definitely shorter sessions! I don't want them sitting there for an hour. Maybe 10 questions at a time? That seems manageable—they can do it in maybe 10-15 minutes and then take a break.

**Dev**: 10 questions per session sounds good. Would you ever want to change that number, or is 10 always fine?

**Sarah**: Hmm, maybe sometimes they'd want to do a quick 5-question review, or if they're really motivated, maybe more. But 10 should be the default.

**Dev**: Okay, so we'll make 10 the default but allow it to be configurable. What range would you want—maybe 5 to 50 questions?

**Sarah**: That sounds reasonable. I can't imagine them wanting to do more than 50 at once!

---

### Question Selection and Randomization

**Dev**: When your kids start a session, how should the questions be selected? Should they go in order, or should they be random?

**Sarah**: Random, definitely. Otherwise they'll just memorize the order instead of actually learning the material.

**Dev**: Good point. And within a single session, should we make sure they don't see the same question twice?

**Sarah**: Oh yes, please! That would be confusing and annoying for them.

**Dev**: Understood. We'll track which questions have been asked during a session to prevent duplicates.

---

### Feedback During the Quiz

**Dev**: When your kids answer a question, what kind of feedback should they get? Should they know immediately if they got it right or wrong?

**Sarah**: Yes, I'd like them to know right away. That way they can learn from their mistakes as they go.

**Dev**: And if they get it wrong, should we just say "incorrect" or should we show them the correct answer?

**Sarah**: Show them the correct answer! That's the whole point of practicing. Maybe even a brief explanation of why that's the right answer, if possible.

**Dev**: We can definitely include that. So immediate feedback with the correct answer and a brief explanation for incorrect responses.

---

### End of Session Results

**Dev**: After they finish all 10 questions, what would you like them to see?

**Sarah**: Their score, obviously. Like "You got 7 out of 10 correct" or something like that.

**Dev**: Would you like to show a percentage as well? Like "70% accuracy"?

**Sarah**: Yes, that would be helpful. Kids understand percentages from school.

**Dev**: What about a breakdown by topic or difficulty? For example, "You got 3 out of 4 Physics questions correct"?

**Sarah**: Oh, that would be nice! It would help them see which areas they need to work on more.

---

### Review of Incorrect Answers

**Dev**: Here's an important question: after the quiz is done, would you like your kids to be able to review the questions they got wrong?

**Sarah**: Yes! That's actually really important. I want them to see which questions they missed and what the right answers were. That's how they'll learn.

**Dev**: So on the results page, we'd show a review section with each question they got wrong, what they answered, and what the correct answer was?

**Sarah**: Exactly. Maybe show the question number, the question itself, what they picked, and what they should have picked.

**Dev**: Should we visually distinguish the wrong answers from the correct ones? Like maybe show their wrong answer in red and the correct answer in green?

**Sarah**: That would be really helpful, yes. Make it obvious what was wrong and what was right.

**Dev**: What if they get a perfect score—all 10 questions correct? Should we still show the review section?

**Sarah**: Hmm, if they got everything right, there's nothing to review, is there? Maybe just show them a congratulations message instead. Something encouraging!

**Dev**: Great idea. So a congratulatory message for a perfect 10 out of 10, and a detailed review section otherwise.

---

### Question Storage

**Dev**: Let's talk about where the questions come from. Do you have questions already, or would you need help creating them?

**Sarah**: I can put together questions from their textbooks and practice tests. I just need to know what format to use.

**Dev**: We could use a simple CSV file—like a spreadsheet that you can edit in Excel or Google Sheets. Each row would be one question with the topic, the question text, the four options, the correct answer, and the difficulty level.

**Sarah**: That sounds manageable. So something like: Physics, "What is the unit of force?", Newton, Joule, Watt, Pascal, Newton, Easy?

**Dev**: Exactly! You've got it. The format would be: topic, question, option1, option2, option3, option4, answer, difficulty.

**Sarah**: Perfect. I can definitely do that.

**Dev**: How many questions do you think you'd start with?

**Sarah**: Maybe 20-30 per subject to start? So around 60-90 total. I can always add more later.

**Dev**: That should work well. We'd want at least 10-20 questions per topic and difficulty combination to ensure good variety.

---

### Technical Requirements

**Dev**: You mentioned you want this to run on your laptop. Do you have a preference for how it looks? Like a command-line application or something with a graphical interface?

**Sarah**: What's easier? I'm not very technical, so something simple would be best.

**Dev**: We could do a web-based interface that runs locally on your laptop. You'd just open a browser and go to a local address. It would look like a regular website but runs entirely on your computer.

**Sarah**: Oh, that sounds nice! The kids are used to using websites. Would it need internet?

**Dev**: No, it would be completely standalone. No internet required once it's set up.

**Sarah**: Perfect. We don't always have reliable internet at home.

**Dev**: And you mentioned it should be simple. Any specific requirements for the look and feel?

**Sarah**: Just clean and easy to use. Nothing cluttered. Maybe a way to navigate back to the start if they want to try a different subject.

**Dev**: We'll include a navigation header on all pages with links to go back home or see information about the app.

---

### Error Handling

**Dev**: What should happen if something goes wrong? For example, if the question file is missing or has errors?

**Sarah**: I'd want to know what went wrong so I can fix it. Don't just crash—show me a helpful error message.

**Dev**: And if there aren't enough questions for a particular topic and difficulty combination?

**Sarah**: Tell me that too. Something like "Not enough questions available for Physics Hard" so I know to add more.

**Dev**: What about if the kids enter something invalid, like typing letters when they should pick a number?

**Sarah**: Just ask them to try again. Don't make them start over—that would be frustrating.

---

### Score Persistence

**Dev**: One more question: do you want to save scores between sessions? Like a history of how they've done over time?

**Sarah**: That would be nice eventually, but for now, just showing the score at the end is fine. Let's keep it simple for the first version.

**Dev**: Understood. Scores will be shown at the end of each session but won't be saved between sessions.

---

### Session Management

**Dev**: If you have multiple kids using the application, should they have separate accounts or profiles?

**Sarah**: Not necessary for now. They can just take turns. Each time they start, it's a fresh session.

**Dev**: So each session is independent—no need to track who's using it?

**Sarah**: Right. Keep it simple.

---

### Time Limits

**Dev**: Should there be any time limits? Like a timer for each question or for the whole quiz?

**Sarah**: No, I don't want to stress them out. Let them take their time and think through the answers.

**Dev**: No time limits it is. They can take as long as they need.

---

### Summary and Confirmation

**Dev**: Let me summarize what we've discussed to make sure I have everything right:

1. **Subjects**: Physics, Chemistry, and Math
2. **Difficulty Levels**: Easy, Medium, and Hard
3. **Question Format**: Multiple choice with 4 options
4. **Session Length**: 10 questions by default, configurable from 5 to 50
5. **Question Selection**: Random, no duplicates within a session
6. **Immediate Feedback**: Show if correct/incorrect, display correct answer with explanation for wrong answers
7. **End Results**: Show score (correct/total), percentage, and breakdown by topic
8. **Review Section**: Show questions answered incorrectly with user's answer and correct answer, visually distinguished
9. **Perfect Score**: Show congratulatory message instead of review section
10. **Question Storage**: CSV file with topic, question, options, answer, and difficulty
11. **Interface**: Web-based, runs locally on laptop, no internet required
12. **Navigation**: Header with Home and About links on all pages
13. **Error Handling**: Graceful error messages for missing files, invalid input, etc.
14. **Score Persistence**: None—scores shown at end of session only
15. **Time Limits**: None
16. **User Profiles**: None—each session is independent

**Sarah**: Yes, that's exactly what I need! You've captured everything perfectly.

**Dev**: Excellent! I'll get started on this and have something for you to review soon. We'll build it in phases—starting with the topic and difficulty selection, then the question flow, and finally the results and review features.

**Sarah**: That sounds great. Thank you so much!

**Dev**: Thank you, Sarah. I'll be in touch with updates.

---

## Requirements Summary

### Functional Requirements Derived

| ID | Requirement |
|----|-------------|
| FR-001 | System MUST allow users to select from predefined topics (Physics, Chemistry, Math) |
| FR-002 | System MUST allow users to select difficulty levels (Easy, Medium, Hard) |
| FR-003 | System MUST randomly select questions matching topic and difficulty criteria |
| FR-004 | System MUST present questions with four multiple choice options |
| FR-005 | System MUST validate user answers against correct answers in CSV file |
| FR-006 | System MUST track user scores and session progress in real-time |
| FR-007 | System MUST provide end-of-session summary with detailed results |
| FR-008 | System MUST handle CSV file parsing with proper error handling |
| FR-009 | System MUST provide immediate feedback on answer correctness |
| FR-010 | System MUST support sessions of 10 questions by default, configurable between 5-50 |
| FR-011 | System MUST show correct answer with brief explanation for incorrect responses |
| FR-012 | System MUST operate without time limits |
| FR-013 | System MUST maintain separate sessions for CLI and web interfaces |
| FR-014 | System MUST provide an About page with application information |
| FR-015 | System MUST provide consistent navigation across all pages |
| FR-016 | System MUST track questions asked within session to prevent duplicates |
| FR-017 | System MUST track each question answered with user's response and correct answer |
| FR-018 | System MUST display Question Review section on results page |
| FR-019 | System MUST show congratulatory message for 100% accuracy |
| FR-020 | System MUST visually distinguish correct and incorrect answers in review |

### Key Entities Identified

- **Question**: Topic, question text, four options, correct answer, difficulty
- **UserSession**: Selected topic, difficulty, questions asked, answers provided
- **Score**: Correct answers, total questions, accuracy percentage
- **QuestionBank**: Collection of questions from CSV with filtering capabilities
- **QuestionReview**: Question number, question text, user answer, correct answer, correctness status

### Technical Constraints

- Standalone application (no external dependencies)
- Runs locally on laptop
- No internet required
- CSV file for question storage
- Web-based interface with browser access

---

*Interview conducted and documented by the development team.*
