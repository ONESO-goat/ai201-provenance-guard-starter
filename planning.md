# AI Text Detection System - Planning

## Project Overview

This project is a Flask-based web application that evaluates submitted text and estimates whether it was likely written by an AI or a human. The system combines multiple detection signals into a single confidence score, presents a transparent label to the user, and allows users to appeal the result for manual review.

---

# Detection Signals

The detector will use two independent signals.

## Signal 1: Repetition & Vocabulary Diversity

### What it measures

This signal measures how repetitive the writing is.

Metrics include:

* Type-token ratio (unique words / total words)
* Frequency of repeated words
* Repeated sentence beginnings

### Output

A normalized score between **0.0 and 1.0**

* 0.0 = highly diverse vocabulary (human-like)
* 1.0 = highly repetitive (AI-like)

Example:

human_text:

```
0.22
```

ai_text:

```
0.81
```

---

## Signal 2: Sentence Structure Consistency

### What it measures

This signal measures how uniform sentence lengths are.

Metrics include:

* Average sentence length
* Standard deviation of sentence lengths

AI-generated text often has sentences of similar length, while human writing tends to vary more naturally.

### Output

A normalized score between **0.0 and 1.0**

* 0.0 = varied sentence lengths
* 1.0 = extremely consistent sentence lengths

Example:

human_writing:

```
0.30
```

ai_writing:

```
0.76
```

---

## Combining Signals

Each signal contributes equally.

Formula:

```
confidence =
(signal1 * 0.5) +
(signal2 * 0.5)
```

Example:

Signal 1 = 0.80

Signal 2 = 0.60

Final confidence:

```
(0.80 × 0.5) + (0.60 × 0.5) = 0.70
```

The confidence score always ranges from **0.0–1.0**.

---

# Uncertainty Representation

The confidence score represents how strongly the detector believes the text resembles AI-generated writing.

Interpretation:

| Score     | Meaning      |
| --------- | ------------ |
| 0.00–0.39 | Likely Human |
| 0.40–0.69 | Uncertain    |
| 0.70–1.00 | Likely AI    |

### Meaning of 0.60

A confidence score of **0.60** means the signals provide mixed evidence. Some characteristics resemble AI writing, while others resemble human writing. The system does not have enough confidence to classify the submission as either AI or human.

These thresholds are intentionally conservative to reduce false positives.

---

# Transparency Label Design

The interface will display one of three labels.

## High Confidence AI

**Label**

```python
{
    "origin": "ai",
    "confidence": 0.82,
    "reason": "The submitted text contains multiple characteristics commonly associated with AI-generated writing."
}
```

---

## High Confidence Human

**Label**


```python
{
    "origin": "human",
    "confidence": 0.18,
    "reason": "The submitted text shows characteristics that are commonly found in human writing."
}
```

---

## Uncertain

**Label**

```python
{
    "origin": "uncertain",
    "confidence": 0.56,
    "reason": "The available evidence is mixed. This submission should not be classified automatically."
}
```

---

# Appeals Workflow

## Who may submit an appeal?

Anyone who submitted text to the detector.

---

## Information collected

* Original text
* Optional explanation from the user
* Timestamp
* Original confidence score
* Original label

---

## What happens after submission?

The appeal:

1. receives a unique appeal ID
2. status changes to **Pending Review**
3. is stored in the application's appeal database/file
4. records submission timestamp

---

## Human Reviewer View

Each appeal should display:

* Appeal ID
* Original submission
* Confidence score
* Signal 1 score
* Signal 2 score
* Original label
* User explanation
* Current status
* Submission timestamp

Possible statuses:

* Pending Review
* Approved
* Rejected

---

# Anticipated Edge Cases

## Edge Case 1

A poem using heavy repetition and intentionally simple vocabulary.

Reason:

The repetition signal may incorrectly assign a high AI score even though the writing is entirely human.

---

## Edge Case 2

Technical documentation written by an experienced engineer.

Reason:

Consistent sentence lengths and repetitive terminology may resemble AI generated writing despite being human authored.

---

## Edge Case 3

AI generated text that has been heavily edited by a human.

Reason:

Editing increases vocabulary diversity and sentence variation, making the detector less confident.

---

## Edge Case 4

Longer text, which means more repeats - more editing - and more content.

Reason:
    long narrative fiction → may inflate AI-likeness
    structured Medium-style essays → may look AI-like
---

# Architecture

## System Diagram

```
                 +-------------------+
                 |      User         |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Flask Web Server  |
                 +---------+---------+
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
+----------------------+        +----------------------+
| Signal 1 Analyzer    |        | Signal 2 Analyzer    |
| Vocabulary Diversity |        | Sentence Consistency |
+----------+-----------+        +----------+-----------+
           |                               |
           +---------------+---------------+
                           |
                           v
                +----------------------+
                | Confidence Calculator|
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Transparency Label   |
                +----------+-----------+
                           |
                           v
                     Results Returned
                           |
                           v
                    Appeal Submission
                           |
                           v
                     Appeal Storage
                           |
                           v
                   Human Review Queue
```

### Submission Flow

Users submit text through the Flask application. The text is analyzed by both detection signals, combined into a confidence score, and returned with the appropriate transparency label.

### Appeal Flow

If the user disagrees with the result, they can submit an appeal. The system stores the original submission, scores, explanation, and review status so a human reviewer can inspect the case later.

---

# AI Tool Plan

## Milestone 3 — Submission Endpoint + First Signal

### Spec sections provided

* Detection Signals
* Architecture diagram

### AI request

Generate:

* Flask application skeleton
* `/submit` endpoint
* Signal 1 function
* JSON response containing Signal 1 score

### Verification

Test with several manually written and repetitive text samples.

Confirm:

* endpoint accepts text
* score stays between 0 and 1
* repetitive text receives higher scores

---

## Milestone 4 — Second Signal + Confidence Scoring

### Spec sections provided

* Detection Signals
* Uncertainty Representation
* Architecture diagram

### AI request

Generate:

* Signal 2 function
* confidence score calculation
* classification logic

### Verification

Test with:

* clearly AI-like text
* clearly human text
* mixed writing

Confirm confidence scores vary meaningfully and map to the correct label category.

---

## Milestone 5 — Production Layer

### Spec sections provided

* Transparency Labels
* Appeals Workflow
* Architecture diagram

### AI request

Generate:

* label generation logic
* `/appeal` endpoint
* appeal storage
* appeal status management

### Verification

Confirm:

* all three transparency labels appear under the correct conditions
* appeal endpoint stores the submission
* appeal status changes to **Pending Review**
* reviewer information includes all required fields

---

# Final Label Review

The label wording has been reviewed for clarity.

Final labels are:

### Likely AI-Generated

```
Likely AI-Generated
Confidence: XX%

The submitted text contains multiple characteristics commonly associated with AI-generated writing.
```

### Uncertain Result

```
Uncertain Result
Confidence: XX%

The available evidence is mixed. This submission should not be classified automatically.
```

### Likely Human-Written

```
Likely Human-Written
Confidence: XX%

The submitted text shows characteristics that are commonly found in human writing.
```

These labels clearly communicate the result while emphasizing that the detector provides an estimate rather than absolute certainty.
