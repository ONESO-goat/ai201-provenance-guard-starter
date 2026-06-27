# AI Text Detection System - Planning

## Project Overview

This project is a Flask-based web application that evaluates submitted text and estimates whether it was likely written by an AI or a human. The system combines multiple detection signals into a single confidence score, presents a transparent label to the user, and allows users to appeal the result for manual review.

## Core Features
* User registration and login
* Story publishing
* AI text analysis
* Confidence scoring
* Transparency labels
* Appeals workflow
* User verification
* Audit logging
* Rate limiting

## Limitations
* The detector provides an estimate, not proof of AI authorship.
* Detection relies on brute force signals rather than a trained machine learning.
* Very short submissions provide limited statistical information.
* Creative writing styles (over the top text or long in length) may resemble AI generated text.

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
    "origin": "likely_ai",
    "confidence": 0.82,
    "reason": "The submitted text contains multiple characteristics commonly associated with AI-generated writing."
}
```

---

## High Confidence Human

**Label**


```python
{
    "origin": "likely_human",
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
* Signal 3 score
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

# Data Storage

The application stores data in JSON files.

Files include:

- users.json
- stories.json
- appeals.json
- audit_log.json

Each file is updated after relevant user actions and serves as storage during application execution.

---

# Rate Limiting

To prevent abuse and ensure fair usage of the publishing system, this application implements rate limiting using Flask-Limiter.

## Implementation

Rate limiting is applied directly to the /publish endpoint using the following configuration:

```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

@app.route("/publish", methods=["POST"])
@limiter.limit("2 per minute;25 per day")
def publish():
...
```
## Limits
* 2 requests per minute per IP address
* 25 requests per day per IP address

These limits are designed to:

- Prevent spam publishing
- Reduce server load from repeated automated requests
- Encourage realistic user behavior patterns
- Rate Limit Behavior

When a user exceeds the allowed request limits, Flask-Limiter automatically blocks the request and triggers a 429 Too Many Requests error.

## Custom error handling
A custom error handler is used to return a consistent JSON response:

```python
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded. Try again later."
    }), 429
```

Example Response (Rate Limit Exceeded)

```python
{
  "error": "Rate limit exceeded. Try again later."
}
```

### Why This Matters

This system ensures:

- Fair usage across all users
- Protection against automated spam or abuse
- Stable performance under high traffic conditions

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
                           |
                           v
                +----------------------+
                |  Signal 3 Analyzer  |
                |    Agent overview    |
                +----------+-----------+
                           |
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

* Signal 1 function
* JSON response containing Signal 1 score

```python
def one(self, text:str):
    ...
```

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

```python
def two(self, text:str):
    ...
```
### Verification

Test with:

* clearly AI-like text
* clearly human text
* mixed writing

Confirm confidence scores vary meaningfully and map to the correct label category.



## Milestone 4.5 — third Signal

### Spec sections provided

* Agent overview
* low/medium/high range (instead of numbering to avoid the agent to provide a direct score)
* Architecture diagram

### AI request

Generate:

* agent overview
* Signal 3 function
* confidence score calculation
* classification logic
* final score created

```python
def three(self, text:str)
```

### Verification

Test with:

* fake AI response
* mixed ranges of lows/mediums/ and highs


---

## Milestone 5 — Production Layer

### loop
1. signup/login
2. create story
3. publish
4. appeal if things are incorrect, or verify your account to avoid false allegations 

### Spec sections provided

* Transparency Labels
* Appeals Workflow
* Architecture diagram

### AI request

Generate:

* label generation logic
* `/publish` endpoint
* story storage
* story status management


### User request
Generate:

* `/appeal` endpoint
* appeal storage
* appeal status management

```python
@app.route("/appeal", methods=["POST"])
@limiter.limit("10 per minute;100 per day") 
def submit_appeal():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Data was not found during publish process"}), 404
    
    Id = random.randint(1000000000, 9999999999)
    
    story_id = data.get("story_id", "")
    details = data.get("details", "")
    if not story_id:
        return jsonify({"error": "Story id was not provided"}), 404
    if not details:
        details = "The user believes the 'AI' mark is incorrect and wants further verification."
        
    story, exist = get_story_by_id(story_id)
    if not exist:
        return jsonify({"error": "Story was not found"}), 404
    
    story['appeal_id'] = Id
    story["appeal_date"] = datetime.now(tz=timezone.utc).isoformat()
    story['details'] = details.lower().strip()
    
    add_appeal(story)
    return jsonify({"message": f"Appeal created by the user '{story['creator']}'", "appeal": story})

    

```


### Verification

Confirm:

* all three transparency labels appear under the correct conditions
* appeal endpoint stores the submission
* appeal status changes to **Pending Review**
* reviewer information includes all required fields

---

# User Verification

For users to avoid obtaining a false allgeation on their work, they can call the "/verify" route to become a trusted member

## purpose

* gain trust from other users
* extra confirmation and protective on their work


## Route

I created a POST flask route using the url "/verify" to keep things simple.

```python
@app.route("/verify", methods=["POST"])
def verify():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User id not found in session"}), 401
    
    user, exist = get_user(user_id)
    if not exist:
        return jsonify({"error": "User not found"}), 404
    
    if user['verified']:
        return jsonify({"message": f"{user['username']} is already verified", "verified": True}), 200
    
    user['verified'] = True
    save_user(user)
    add_to_audit_log({
        "event": "user_verified_toggle",
        "id": user['id'],
        "user": user['username'],
        "status": True,
        "timestamp": datetime.now(tz=timezone.utc)
    })
    return jsonify({"message": f"{user['username']} is now verified", "verified": True}), 200
    

```
---


# Audit Log

## Overview

The system maintains an audit log to record all important actions that occur within the application. This provides a transparent, chronological history of system behavior and user activity.

Unlike stored user data (accounts or stories), the audit log focuses on events, not final state.

## Purpose

The audit log is used to:

- Track all story publishing events
- Record classification results from the detection system
- Log user verification changes
- Support debugging and transparency
- Provide a complete history for review during moderation or appeals
- Structure

Each audit log entry is stored as a JSON object containing:

- event: type of system action
- user: username performing the action
- story_id (if applicable)
- attribution: AI detection result (if applicable)
- confidence: model confidence score (if applicable)
- status (if applicable)
- timestamp: ISO 8601 time of event

### Example Audit Log

```python
[
    {
        "event": "story_published",
        "user": "joey",
        "story_id": "827a3205-aa22-4ed7-92df-86d7a4e51537",
        "attribution": "likely_human",
        "confidence": 0.26,
        "timestamp": "2026-06-27T20:19:35Z"
    },
    {
        "event": "story_published",
        "user": "joey",
        "story_id": "99291824-83c0-422c-8a5b-66751c7beaaf",
        "attribution": "uncertain",
        "confidence": 0.51,
        "timestamp": "2026-06-27T20:33:01Z"
    },
    {
        "event": "user_verified_toggle",
        "user": "joey",
        "status": true,
        "timestamp": "2026-06-27T20:40:00Z"
    }
]
```
## Event Types

The system currently logs the following event types:

* Story Events
* story_published
* User Events
* user_verified_toggle
* Future Events (planned)
* appeal_submitted
* appeal_resolved
* classification_updated
* Integration with System

Audit log entries are created automatically during key actions:

- When a story is published → story_published
- When a user toggles verification → user_verified_toggle
- When classification is generated → included in publish event metadata

## Why This Matters

### The audit log ensures:

* Full transparency of system decisions
* Traceability of AI classification results
* Accountability for user actions
* Easier debugging and moderation review

---

# Final Label Review

The label wording has been reviewed for clarity.

Final labels are:

### Likely AI-Generated

```
likely_ai
Confidence: X.XXX

The submitted text contains multiple characteristics commonly associated with AI-generated writing.
```

### Uncertain Result

```
uncertain
Confidence: XX%

The available evidence is mixed. This submission should not be classified automatically.
```

### Likely Human-Written

```
likely_human
Confidence: XX%

The submitted text shows characteristics that are commonly found in human writing.
```

These labels clearly communicate the result while emphasizing that the detector provides an estimate rather than absolute certainty.




# Results

SEQUENCE SCORES: 
        - signal 1 0.6470852017937218 
        - signal 2 0.025781354795439294 
        - OVERALL 0.33643327829458053 
        - AI -0.1

FINAL SCORE: 0.23643327829458052