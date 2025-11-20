# Nonprofit CRM Frontend

A Next.js frontend application for the Nonprofit CRM system, featuring AI-powered donor message generation.

## Features

- **MessageGenerator Component**: Generate personalized donor messages with AI
- **Inline Editing**: Edit generated messages directly in the interface
- **Copy to Clipboard**: One-click copying of messages
- **Regenerate Variations**: Generate alternative message phrasings
- **Multiple Tones**: Choose from professional, friendly, or formal tones
- **Responsive Design**: Beautiful, modern UI built with Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Building for Production

```bash
npm run build
npm start
```

## Component Usage

### MessageGenerator

The `MessageGenerator` component allows fundraisers to generate, edit, and copy personalized donor messages.

```tsx
import MessageGenerator from '@/components/MessageGenerator';

function DonorPage() {
  return (
    <MessageGenerator
      constituentId="123"
      initialTone="professional"
      onMessageGenerated={(message) => {
        console.log('Generated:', message);
      }}
    />
  );
}
```

#### Props

- `constituentId` (string, required): The ID of the constituent/donor
- `initialTone` (string, optional): Initial tone selection ('professional' | 'friendly' | 'formal')
- `onMessageGenerated` (function, optional): Callback when a message is generated

#### Features

1. **Generate Messages**: Click "Generate Message" to create a personalized message
2. **Edit Inline**: Modify the generated text directly in the textarea
3. **Copy to Clipboard**: Click "Copy Message" to copy the text
4. **Regenerate**: Click "Regenerate" for alternative variations
5. **Change Tone**: Select different tones from the dropdown

## API Routes

### POST /api/constituents/[id]/message

Generate a personalized message for a constituent.

**Request Body:**
```json
{
  "tone": "professional",
  "occasion": "general outreach",
  "context": "optional context"
}
```

**Response:**
```json
{
  "message": "Generated message text...",
  "constituentId": "123",
  "generatedAt": "2024-01-01T00:00:00.000Z"
}
```

## Technology Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **react-textarea-autosize**: Auto-growing textareas

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── constituents/
│   │       └── [id]/
│   │           └── message/
│   │               └── route.ts       # Message generation API
│   ├── globals.css                    # Global styles
│   ├── layout.tsx                     # Root layout
│   └── page.tsx                       # Home page
├── components/
│   └── MessageGenerator.tsx           # Main component
├── public/                            # Static assets
├── next.config.js                     # Next.js configuration
├── tailwind.config.js                 # Tailwind configuration
├── tsconfig.json                      # TypeScript configuration
└── package.json                       # Dependencies
```

## Future Enhancements

- [ ] Connect to AI service (OpenAI, Anthropic) for real message generation
- [ ] Integrate with backend database to fetch constituent data
- [ ] Add message history and saved templates
- [ ] Support for multiple languages
- [ ] Analytics and message effectiveness tracking
- [ ] A/B testing for message variations

## Integration with Python Backend

The frontend is designed to work alongside the existing Python/SQLAlchemy backend. To integrate:

1. Update the API route to query the PostgreSQL/SQLite database
2. Fetch constituent data (name, giving history, interactions)
3. Pass relevant context to an AI service for personalization
4. Store generated messages in the interactions table

Example integration:

```typescript
// In route.ts
import { PythonShell } from 'python-shell';

// Query database via Python
const constituent = await queryDatabase(constituentId);

// Generate with AI service
const message = await generateWithAI({
  name: constituent.name,
  givingHistory: constituent.totalGiving,
  lastInteraction: constituent.lastInteraction,
  tone: requestTone
});
```

## License

This is a proof-of-concept for educational purposes.
