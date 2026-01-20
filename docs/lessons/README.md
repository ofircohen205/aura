# Educational Lessons for Aura RAG System

This directory contains comprehensive, beginner-friendly educational lessons for Python, TypeScript, and Java programming languages. These lessons are designed to be ingested into the RAG (Retrieval-Augmented Generation) vector database to support the struggle detection workflow's lesson generation capabilities.

## Structure

Lessons are organized by language and difficulty level:

```
docs/lessons/
├── python/
│   ├── beginner/      (10 lessons)
│   ├── intermediate/  (10 lessons)
│   └── advanced/      (10 lessons)
├── typescript/
│   ├── beginner/      (10 lessons)
│   ├── intermediate/  (10 lessons)
│   └── advanced/      (10 lessons)
└── java/
    ├── beginner/      (10 lessons)
    ├── intermediate/  (10 lessons)
    └── advanced/      (10 lessons)
```

## Lesson Format

Each lesson is a Markdown file with YAML frontmatter containing metadata:

```markdown
---
title: "Lesson Title"
language: python|typescript|java
difficulty: beginner|intermediate|advanced
prerequisites: []
keywords: []
---

# Learning Objectives

- Objective 1
- Objective 2

# Prerequisites

- Previous lesson or concept

# Introduction

Brief introduction to the topic

# Core Concepts

## Concept 1

Explanation with examples

# Common Mistakes

- Mistake 1 and how to avoid it

# Practice Exercises

1. Exercise 1

# Key Takeaways

- Takeaway 1

# Related Topics

- Link to related lessons
```

## Difficulty Levels

### Beginner

- Fundamentals and basic concepts
- Simple examples and explanations
- Focus on understanding core concepts
- Minimal prerequisites

### Intermediate

- Building on fundamentals
- More complex examples
- Introduction to patterns and best practices
- Some prerequisites expected

### Advanced

- Complex topics and patterns
- Real-world applications
- Performance considerations
- Requires solid foundation

## Usage

### Ingesting Lessons into RAG

Use the Aura CLI to ingest lessons:

```bash
# Ingest all lessons
aura rag ingest docs/lessons/

# Ingest lessons for a specific language
aura rag ingest docs/lessons/python/

# Ingest lessons for a specific difficulty level
aura rag ingest docs/lessons/python/beginner/
```

### Querying Lessons

The RAG system will automatically retrieve relevant lessons based on:

- Error patterns in student code
- Edit frequency and struggle indicators
- Language detection (if available)
- Difficulty level matching

## Learning Paths

See [INDEX.md](./INDEX.md) for complete lesson index and learning paths for each language.

## Contributing

When adding new lessons:

1. Follow the lesson format template
2. Include appropriate frontmatter metadata
3. Ensure examples are correct and runnable
4. Keep content beginner-friendly for beginner lessons
5. Add cross-references to related topics
6. Update INDEX.md with new lessons

## Metadata Fields

- **title**: Clear, descriptive lesson title
- **language**: `python`, `typescript`, or `java`
- **difficulty**: `beginner`, `intermediate`, or `advanced`
- **prerequisites**: List of prerequisite lesson titles or concepts
- **keywords**: List of relevant keywords for better retrieval
