A key limitation is that simulated falls differ from genuine fall events in both magnitude and trajectory. Accordingly, the model will be trained to detect high-magnitude displacement events rather than clinically defined falls, and all performance claims will be scoped correspondingly.
3. Sensing Concept
The experiment utilises the onboard BMI270 inertial measurement unit, which provides triaxial accelerometers and gyroscope data. Inertial sensing is well-suited to this application due to its low power consumption, continuous availability, and sensitivity to whole-body motion dynamics.
A key design element is the addition of a hardware pre-filter gate that uses composite acceleration magnitude. Inference only happens when the signal goes over a certain level, which is usually 1.8g. This method cuts down on unnecessary calculations when there is no motion and lowers the chance of false positives that come with low-amplitude motion.
By incorporating domain knowledge into the sensing pipeline, the system avoids treating all inputs as equally informative, thereby improving both efficiency and robustness without increasing model complexity.

4. System Architecture and Pre-processing
To provide a clear structural overview of the proposed system, Figure 1 presents the end-to-end on-device inference pipeline. The diagram highlights the sequential data flow from inertial sensing through pre-filter gating, feature extraction, and classification. Of particular importance is the inclusion of a pre-filter gate, which enables event-driven inference by suppressing low-magnitude signals before model execution.

Figure 1: Block diagram of the proposed TinyML
As illustrated in Figure 1, the system departs from conventional always-on inference pipelines by introducing a gating mechanism before windowing and feature extraction. This design decision is motivated by the fact that this approach improves both computational efficiency and energy use by reducing the frequency of model invocation while maintaining responsiveness to high-magnitude events. The subsequent sections formalise each stage of the pipeline in detail.
4.1 Processing Pipeline
The system works as a smart, event-driven setup. It constantly checks movement data 50 times a second and uses a built-in filter to spot significant changes in acceleration. When the movement hits a certain level, the system saves a one-second snapshot of data to look at more closely. From this snapshot, it pulls out key details, or "features", to understand what is happening. These details are then cleaned up using settings from earlier testing and sent to a compact AI model, built with TensorFlow Lite for Microcontrollers, to figure out the type of activity. To keep things accurate, the system only reports a result if the AI is sure enough about its prediction. In every one-second window, the system looks at about 30 different markers, like the average movement or the highest peaks, which helps it stay efficient while still getting the full picture.
4.2 Window Length and Latency
A one-second window introduces a minimum detection latency of one second. While this period does not constitute an instantaneous response, it represents a bounded and predictable delay suitable for demonstration purposes. The system is therefore characterised as near-real-time, with latency explicitly measured and reported.
4.3 Memory Management Strategy
Memory constraints constitute a primary limiting factor in deploying machine learning pipelines on microcontroller-class devices. The Arduino Nano 33 BLE Sense Rev2 provides 256 KB of SRAM; however, only a reduced portion of this memory is available for application-level allocation due to system-level reservations and runtime overhead. Consequently, the design of the inference pipeline must explicitly account for memory partitioning across stack usage, static variables, feature buffers, and the TensorFlow Lite for Microcontrollers runtime. Figure 2 illustrates the adopted memory layout, highlighting both the distribution of components and the constrained operational envelope within which the system must function.

Figure 2: SRAM memory layout for the deployed TinyML system 
Figure 2 shows that the tensor arena is the most important part of the runtime allocation. This is because it stores intermediate activations and temporary buffers that are needed during inference. This puts strict limits on the model architecture, which means that the network design has to be small and the quantisation has to be strong. Efficient feature engineering is very important because the small amount of memory set aside for feature buffers ensures that useful representations are extracted without using too much memory. Furthermore, the absence of dynamic memory allocation eliminates fragmentation risks and ensures predictable execution, which is vital for reliable embedded deployment. Maintaining a modest memory buffer further enhances system stability, particularly when managing interrupt-driven workloads and real-time sensor data acquisition.

5. Machine Learning Model
5.1 Architecture
A lightweight fully connected neural network is employed, consisting of:
Input layer (~30 features)
One hidden layer (32 neurons, ReLU activation)
Output layer (softmax over four classes)
This architecture is selected to balance representational capacity with memory constraints. For structured, feature-engineered inputs, deeper architectures offer limited benefit relative to their resource cost.
5.2 Memory Budget
The primary engineering constraint is SRAM availability (256 KB total). Estimated usage is as follows:
TFLite Microinterpreter: ~20–30 KB
Tensor arena: ~15–25 KB
Feature buffer: ~1 KB
Stack and globals: ~10–20 KB
Memory allocation must be carefully profiled. The tensor arena size will be determined empirically, as insufficient allocation results in runtime failure with limited diagnostic feedback.
5.3 Quantisation
Post-training INT8 quantisation will be applied to reduce the model size and improve inference efficiency. This typically achieves approximately fourfold compression. The impact on accuracy will be evaluated by comparing quantised and floating-point models on a held-out dataset.

6. Known Limitations and Mitigation Strategies
Key limitations are identified and addressed as follows:
SRAM constraints: Managed through careful profiling and tensor arena optimisation
Simulated fall validity: Reframed as high-magnitude displacement detection
Single-user data: Acknowledged as a limitation; mitigated through multi-session collection
Confidence inflation: Addressed by holding out entire sessions for evaluation
Debugging constraints: Mitigated through prior validation in Python
Lack of hardware acceleration: Addressed through explicit latency measurement
Importantly, these limitations are not treated as shortcomings but as defining constraints of the problem space, shaping both system design and evaluation methodology.
7. Feasibility Assessment
The project is considered feasible under the following conditions:
Accurate tensor arena sizing before full deployment
Exclusive use of device-native data for training
Rigorous evaluation using held-out sessions
Conservative and evidence-based performance claims
While technical risks primarily involve memory management, scientific risks pertain to dataset quality and generalisation; both remain manageable within the project's scope.

8. Expected Outcomes
The project is expected to deliver the following:
A fully functional on-device inference pipeline
Inference latency below 50 ms per window
Classification accuracy exceeding 85% on held-out data
A complete confusion matrix for performance analysis
Reproducible training and evaluation scripts
Instant, filtered reporting, showing only predictions the system is confident about.
The outcome is a validated embedded ML system, not a production-ready safety device. Energy efficiency will be approximated using duty-cycle analysis, comparing continuous inference against gated inference to quantify computational savings.

9. Conclusion
This study presents a constraint-aware implementation of machine learning on a microcontroller platform. It demonstrates a grounded understanding of TinyML capabilities under realistic conditions. The study distinguishes focus not on maximising performance in ideal settings but on characterising what is achievable within strict hardware constraints. In doing so, it provides both practical insights for system developers and a contribution to the study of AI at the lowest tier of computational infrastructure.
