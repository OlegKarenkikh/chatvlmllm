# Adding Example Documents

## Important Privacy Notice

⚠️ **DO NOT** upload real documents containing:
- Personal information (names, addresses, phone numbers)
- Financial data (account numbers, credit card info)
- Official documents (passports, IDs, licenses)
- Confidential business information

## How to Add Examples

### Option 1: Use Synthetic Documents

Create fake documents for testing:

1. **Online Generators**
   - Invoice generators: invoice-generator.com
   - Receipt generators: receiptmakerly.com
   - Form generators: pdfcrowd.com

2. **Design Tools**
   - Canva: Create custom document templates
   - Figma: Design realistic mockups
   - Google Docs: Create and export as images

### Option 2: Use Public Datasets

- **FUNSD**: Form Understanding in Noisy Scanned Documents
- **SROIE**: Scanned Receipts OCR and Information Extraction
- **RVL-CDIP**: Document classification dataset

### Option 3: Create Your Own

Use sample data:
```
Company: ACME Corporation
Invoice #: INV-2024-001
Date: 2024-01-15
Total: $1,234.56
```

## Folder Structure

```
examples/
├── passports/
│   └── sample_passport.jpg
├── invoices/
│   ├── invoice_001.jpg
│   └── invoice_002.png
└── receipts/
    └── receipt_sample.jpg
```

## File Naming Convention

- Use descriptive names: `invoice_electronics_2024.jpg`
- Include document type: `receipt_grocery_store.png`
- Add quality indicator: `passport_highres.jpg`
- Avoid special characters

## Testing Your Examples

1. Upload to appropriate folder
2. Run OCR mode in the application
3. Verify text extraction
4. Check field parsing accuracy
5. Document results in research log

## Sharing Examples

When contributing:
- Ensure privacy compliance
- Provide attribution for public datasets
- Include metadata (resolution, quality, source)
- Add description in pull request