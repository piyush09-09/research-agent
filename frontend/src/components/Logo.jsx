export default function Logo({ size = 32 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="32" height="32" rx="8" fill="#13161c" stroke="#1e2230" strokeWidth="1" />
      <path
        d="M9 12 L16 8 L23 12 L23 20 L16 24 L9 20 Z"
        stroke="#4a7cff"
        strokeWidth="1.5"
        fill="none"
        strokeLinejoin="round"
      />
      <path
        d="M16 8 L16 24"
        stroke="#4a7cff"
        strokeWidth="1.5"
        opacity="0.4"
      />
      <path
        d="M9 12 L23 20 M23 12 L9 20"
        stroke="#4a7cff"
        strokeWidth="1.5"
        opacity="0.25"
      />
      <circle cx="16" cy="16" r="2.5" fill="#4a7cff" opacity="0.9" />
    </svg>
  );
}