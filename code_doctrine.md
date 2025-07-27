# Code Doctrine

**Michael Banovac**

**June 2025**

---

## **I. Introduction**

A Template for the Formulation of a Programming Language Code Doctrine

This template serves as the foundation for establishing a code doctrine: a comprehensive system of rules, parameters, considerations, guidelines, and axiomatic programming principles to be observed and enforced when generating code for game development in Godot using GDScript, or alternative frameworks employing Rust, or other suitable languages as determined by project requirements.

## **II. Fundamental Doctrine of Wide Application**

These considerations constitute the philosophical foundation upon which all code shall be constructed, regardless of application, development environment, use case, or programming language. They represent immutable first principles, applicable under all circumstances and conditions. Code that deviates from these principled foundations should be regarded with suspicion and subjected to rigorous examination, for these principles serve to guide a project from inception to completion in the elegant and reasoned structuring of all code---from syntax and styling to coherency, organization, and the code's role as the clear and simple vehicle that carries the program, software, or game with performance, precision, organization, and clarity.

The craft of writing code constitutes the primary means of effectual change within the development environment. Each line written shapes the final work and determines its lasting value.

### **Preservation Axiom**

> Games shall be distributed upon DVD media containing the complete, functional game, with Blu-Ray discs employed only when larger projects necessitate such capacity. Code must be engineered with the fundamental understanding that the entire game shall remain properly playable and installable from physical media without external dependencies, activation requirements, or reliance upon remote services. Direct installation methods apart from disc media shall also be provided, ensuring multiple pathways to game preservation and access.

## **III. The First Principles**

### **Principle I: Code Should be Coherent**

Code must be written with utmost clarity, employing the most intuitive, logical, and proper methodologies to accomplish the task at hand. Confusing or obfuscated code that merely fulfills the letter of requirements while violating the spirit of understanding shall be rejected. Every line, function, and construct must include commentary that clearly defines its necessity, its function within the project's scope, and the practical effect it produces during gameplay or system operation. When code performs functions invisible to the player, such hidden operations must be thoroughly explained. All code must provide commentary sufficient for any reader to comprehend its purpose and method. The source code and project files, being shipped alongside the game, should present themselves as exemplars of the craft---understandable, clear, elegant in presentation, and readily apparent in function to any curious mind, whether child, scholar, or fellow craftsman.

### **Principle II: Code Should be Performant**

Code must not consume system resources unnecessarily through careless construction. Such waste leads to degraded gameplay experience, difficult project management, and arduous optimization tasks during later development phases. Code shall, whenever possible, maximize performance and optimization to ensure smooth operation under all circumstances. This principle applies universally---whether crafting a simple game of Tetris or an adventure of Monster Hunter's scope, performance excellence remains paramount. Code must not be written with the expectation that other project elements will compensate for its inefficiencies.

### **Principle III: Code Should be Modular**

Code must be constructed with the expectation of self-contained operation within its designated sphere. Whenever feasible, code should be easily removable, modifiable, replicable, and insertable without extensive alteration of surrounding systems. Dependencies, interconnected webs, and entangled relationships that necessitate comprehensive rebuilds for simple changes shall be avoided. Code should function as discrete, transportable units---akin to cartridges or physical media that can be inserted, removed, or replaced with minimal disruption to the greater whole.

### **Principle IV: Code Should be Precise**

Code must accomplish its intended purpose without unnecessary complexity or redundancy. Each construct should serve a clear and definite function within the project's architecture. When verbose implementation becomes necessary for a particular task, such expansion must be justified by clear benefit to the overall work and must not violate other fundamental principles. Precision demands that every element serve its purpose efficiently, yet clarity shall take precedence over mere brevity when these virtues conflict.

### **Principle V: Code Should be Scalable**

Code must be designed from the outset to accommodate growth and increased demands. Initial implementations should possess the capacity to handle substantial increases in data, input, users, or other scaling factors. Every function should be capable of withstanding stress testing and crucible examinations that challenge its foundational capabilities. This principle must be maintained consistently throughout development, from the first lines written to the final implementations.

### **Principle VI: Code Should be Logical**

Code must follow rational methodologies and avoid illogical or unnecessarily complex approaches when simpler, more rational solutions exist. Adherence to logic ensures that code remains comprehensible and maintainable while supporting all other fundamental principles.

### **Principle VII: Code Should be Idiomatic**

Code must conform to the established patterns, conventions, and philosophical approaches of its chosen language and version. Rather than imposing foreign paradigms upon a language, code should leverage each language's inherent strengths and embrace its natural idioms. When transitioning between languages---from GDScript to Rust, for instance---the approach should adapt to honor each language's unique philosophy rather than forcing uniformity where none should exist.

### **Principle VIII: Code Should be Adaptable**

Code must be constructed with the understanding that initial implementations rarely represent final forms. While maintaining adherence to all other principles, code should accommodate evolution, modification, and extension throughout the development lifecycle. Features should be designed to support iteration, addition, and even removal when necessary. The architecture should remain flexible enough to support post-release content, modifications, and long-term preservation requirements while maintaining structural integrity.

### **Principle IX: Code Should be Elegant**

Code must be crafted with excellence as its ultimate aim, serving as a testament to the beauty of reasoned design and the nobility of the programming craft. When viewed by others, code should inspire admiration for its simplicity and architectural grandeur, from its smallest components to its overarching structure. All preceding principles should contribute to this ultimate goal, creating works that stand as masterpieces of design and functionality, regardless of whether the game's scope is humble or rivals the greatest achievements of larger studios.

### **Principle X: Code Should be Resilient**

Code must be architected with a profound awareness of its potential for failure. This principle demands a proactive design approach, where comprehensive risk analysis identifies potential failure points---whether from external data corruption, unexpected user input, or internal system errors. Robust error handling and mitigation strategies shall be implemented not as afterthoughts, but as integral components of the design. The application must, whenever possible, exhibit graceful degradation, ensuring that the failure of a non-essential component does not compromise the stability of the whole. Through this discipline, which is verified by extensive quality assurance and testing, code becomes not merely functional, but resilient---capable of withstanding the rigors of real-world use and preserving a coherent user experience even in the face of adversity.

## **IV. Principle Hierarchy for Conflict Resolution**

When principles conflict during implementation, the following hierarchy shall guide decision-making:

### **Universal Priorities (Applicable to All Games)**

> - **Coherent** - Readability and maintainability form the foundation of all enduring code
> - **Performant** - Player experience remains paramount and must not be compromised
> - **Modular** - Long-term maintainability and preservation depend upon modular construction

### **Contextual Priorities (Applied According to Project Needs)**

> - **Precise** - Avoid unnecessary complexity while maintaining clarity
> - **Scalable** - Consider growth requirements based on project scope and ambition
> - **Logical** - Maintain rational approaches in all implementations
> - **Idiomatic** - Honor language conventions and established patterns
> - **Adaptable** - Design for evolution and adaptation
> - **Elegant** - Strive for beauty in design and implementation
> - **Resilient** - Engineer for stability and graceful failure

When universal priorities conflict among themselves, favor the principle that best serves the game's core function and player experience. When contextual priorities conflict, consider the specific needs of the current project phase and long-term goals.

## **V. Application and Enforcement**

> This doctrine shall be applied consistently throughout all development phases, from initial concept through final release and beyond. Regular review of code against these principles ensures adherence and identifies opportunities for refinement. The principles serve not as constraints but as guideposts toward excellence, directing the craft of programming toward its highest expression. Let this doctrine stand as both foundation and aspiration---a framework for creating games that honor the craft of programming while serving players with excellence, now and for generations to come.

