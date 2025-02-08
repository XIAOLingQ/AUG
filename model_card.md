---
language:
- en
tags:
- uml
- software-engineering
- requirements-modeling
- glm4
- code-generation
license: apache-2.0
---
# AUG - Automated UML Model Generation

AUG (Automated UML Model Generation) is a fine-tuned version of GLM4-9B specifically designed for generating UML diagrams from natural language requirements. It supports class diagrams, use case diagrams, and sequence diagrams generation with high accuracy.

## Model Description

- **Model Type:** Fine-tuned GLM4-9B
- **Language(s):** English
- **Task:** UML Diagram Generation
- **License:** Apache 2.0

### Training Data

The model was trained on a comprehensive dataset of software requirements and their corresponding UML diagrams, focusing on:

- Class diagrams
- Use case diagrams
- Sequence diagrams

## Performance and Limitations

### Metrics

The model achieves the following performance metrics:

- Precision: 78.68%
- Recall: 67.37%
- F1 Score: 72.59%

Compared to ChatGPT 4.0, AUG shows improved performance in:

- Recall rate
- Overall F1 score

### Limitations

While the model performs well, users should be aware that:

- The model's output may still require human verification
- Complex software architectures might need additional refinement
- Performance may vary based on the clarity of input requirements

## Training Procedure

The model was fine-tuned from GLM4-9B using:

- Specialized UML diagram dataset
- Requirements-to-diagram mapping
- Clarification dialogue patterns

## Additional Information

- **GitHub Repository:** https://github.com/XIAOLingQ/AUG
- **Demo Video:** https://youtu.be/kHbCPK6kOag

## Acknowledgements

This model was developed by researchers from Wuhan Textile University and Wuhan University. Special thanks to all contributors and the open-source community.
