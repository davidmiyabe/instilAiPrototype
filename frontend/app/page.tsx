import MessageGenerator from '@/components/MessageGenerator';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Nonprofit CRM
          </h1>
          <p className="text-lg text-gray-600">
            Generate personalized messages for your donors
          </p>
        </div>

        <MessageGenerator
          constituentId="123"
          initialTone="professional"
          onMessageGenerated={(message) => {
            console.log('Message generated:', message);
          }}
        />
      </div>
    </main>
  );
}
