- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	Project: Python invoice processing application using Donut transformer model
	Language: Python 3.11+
	Features: Process invoices from local path, extract data as JSON output
	Model: Donut (naver-clova-ix/donut-base-finetuned-cord-v2)

- [x] Scaffold the Project
	Created project structure with:
	- src/invoice_processor.py (main processing logic)
	- src/__init__.py (package initialization)
	- main.py (CLI entry point)
	- config.json (configuration)
	- requirements.txt (dependencies)
	- invoices/ (input directory)
	- output/ (output directory)

- [x] Customize the Project
	Implemented InvoiceProcessor class with:
	- Donut model integration via HuggingFace Transformers
	- Single invoice and batch processing capabilities
	- GPU/CPU device detection
	- JSON output generation
	- Configurable model parameters

- [x] Install Required Extensions
	No specific extensions required for this Python project.

- [x] Compile the Project
	Dependencies listed in requirements.txt:
	- torch>=2.0.0
	- transformers>=4.30.0
	- pillow>=10.0.0
	- sentencepiece>=0.1.99
	- accelerate>=0.20.0
	- python-dateutil>=2.8.2
	
	To install: pip install -r requirements.txt

- [x] Create and Run Task
	Not required - Python script execution via command line.

- [x] Launch the Project
	Run with: python main.py
	Options:
	  --input: Input directory or single file
	  --output: Output directory for JSON results
	  --config: Configuration file path
	  --single: Process single file mode

- [x] Ensure Documentation is Complete
	README.md contains:
	- Project overview and features
	- Installation instructions
	- Usage examples
	- Configuration guide
	- Output format documentation
	- Troubleshooting tips
