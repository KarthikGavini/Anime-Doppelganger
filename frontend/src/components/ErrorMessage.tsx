interface ErrorMessageProps {
  message: string;
}

export default function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="bg-red-500 text-white px-4 py-2 rounded-md shadow-md text-center mt-4">
      {message}
    </div>
  );
}
