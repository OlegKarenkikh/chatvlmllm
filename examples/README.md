# Example Documents

This directory contains sample documents for testing the OCR and VLM capabilities of ChatVLMLLM.

## Directory Structure

```
examples/
├── passports/          # Sample passport documents
├── invoices/           # Sample invoices and bills
├── receipts/           # Sample receipts
├── forms/              # Sample forms and applications
└── technical/          # Technical documents and papers
```

## Usage

### Testing OCR

1. Open the ChatVLMLLM application
2. Navigate to OCR Mode
3. Upload a sample document from this directory
4. Select the appropriate document type
5. Click "Extract Text" to process

### Testing Chat Mode

1. Open the ChatVLMLLM application
2. Navigate to Chat Mode
3. Upload a sample document
4. Ask questions about the document content

## Sample Queries

### For Invoices
- "What is the total amount on this invoice?"
- "When is the payment due?"
- "Who is the vendor?"
- "List all items with their prices"

### For Passports
- "Extract all personal information"
- "What is the expiry date?"
- "What is the passport number?"

### For Receipts
- "What items were purchased?"
- "What is the total amount?"
- "When was this purchase made?"

## Adding Your Own Examples

Feel free to add your own test documents to this directory. Supported formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

**Note**: Please ensure you have the right to use and share any documents you add.

## Privacy Notice

The example documents provided are either:
1. Synthetic/generated samples
2. Publicly available documents
3. Anonymized real documents

Do not upload sensitive or confidential documents without proper authorization.

## Dataset Attribution

If you use public datasets, please provide attribution:

- **[Dataset Name]**: Source and license information
- **[Dataset Name]**: Source and license information

## Creating Test Cases

### Ground Truth Format

For each test image, you can create a corresponding `.json` file with ground truth:

```json
{
  "filename": "invoice_001.jpg",
  "type": "invoice",
  "fields": {
    "invoice_number": "INV-2026-001",
    "date": "2026-01-15",
    "total": "1234.56",
    "vendor": "Example Corp"
  },
  "full_text": "Complete text content..."
}
```

This allows for automated testing and accuracy measurement.