"""Stimulus Analysis: Upon receiving a stimulus (e.g., a question), the Top Agent first analyzes the input using the reflection module to extract key elements.

Memory Retrieval: The extracted elements are passed to the Memory Agent for retrieving relevant memories, which are stored in the Working Memory.

Coordination with Thinking and Emotion Agents: The Top Agent sends the relevant memories and the question to the Thinking Agent and Emotion Agent for logical and emotional analysis.

Response Formulation: Based on the contents in the Working Memory, the Top Agent formulates an appropriate response for the conversation.

Context Management: Manages the context window by transferring content that cannot fit into the Working Memory to Short Memory, which is later converted into long-term memory through rehearsal."""