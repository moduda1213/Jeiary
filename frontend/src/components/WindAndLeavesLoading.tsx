import { motion } from "motion/react";

interface Leaf {
  id: number;
  x: number;
  delay: number;
  duration: number;
  rotation: number;
  color: string;
}

export function WindAndLeavesLoading() {
  // 다양한 낙엽 생성
  const leaves: Leaf[] = [
    { id: 1, x: 50, delay: 0, duration: 3, rotation: 360, color: "#D97706" },
    { id: 2, x: 150, delay: 0.5, duration: 3.5, rotation: -360, color: "#DC2626" },
    { id: 3, x: 250, delay: 1, duration: 3.2, rotation: 360, color: "#EA580C" },
    { id: 4, x: 100, delay: 1.5, duration: 3.8, rotation: -360, color: "#B91C1C" },
    { id: 5, x: 200, delay: 0.3, duration: 3.3, rotation: 360, color: "#F59E0B" },
    { id: 6, x: 300, delay: 0.8, duration: 3.6, rotation: -360, color: "#92400E" },
    { id: 7, x: 75, delay: 1.2, duration: 3.4, rotation: 360, color: "#C2410C" },
    { id: 8, x: 175, delay: 0.2, duration: 3.7, rotation: -360, color: "#EA580C" },
  ];

  return (
    <div className="relative w-[400px] h-[400px] bg-gradient-to-b from-sky-100 to-blue-50 rounded-lg overflow-hidden">
      {/* 바람 효과 라인들 */}
      <div className="absolute inset-0">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={`wind-${i}`}
            className="absolute h-0.5 bg-white/30"
            style={{
              top: `${20 + i * 20}%`,
              left: 0,
              width: "60%",
            }}
            animate={{
              x: [0, 400],
              opacity: [0, 0.5, 0],
            }}
            transition={{
              duration: 2,
              delay: i * 0.4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* 낙엽들 */}
      {leaves.map((leaf) => (
        <motion.div
          key={leaf.id}
          className="absolute"
          style={{
            left: leaf.x,
            top: -20,
          }}
          animate={{
            y: [0, 420],
            x: [
              0,
              Math.sin((leaf.delay * Math.PI) / 2) * 60,
              Math.sin((leaf.delay * Math.PI) / 2 + 1) * -40,
              Math.sin((leaf.delay * Math.PI) / 2 + 2) * 50,
              0,
            ],
            rotate: [0, leaf.rotation],
          }}
          transition={{
            duration: leaf.duration,
            delay: leaf.delay,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          <svg
            width="30"
            height="30"
            viewBox="0 0 30 30"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M15 3C15 3 12 8 12 12C12 16 8 18 4 18C8 18 12 20 12 24C12 28 15 33 15 33C15 33 18 28 18 24C18 20 22 18 26 18C22 18 18 16 18 12C18 8 15 3 15 3Z"
              fill={leaf.color}
              opacity="0.8"
            />
            <path
              d="M15 3L15 33"
              stroke={leaf.color}
              strokeWidth="1"
              opacity="0.5"
            />
          </svg>
        </motion.div>
      ))}

      {/* 로딩 텍스트 */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          className="text-2xl text-gray-700 bg-white/80 px-6 py-3 rounded-full backdrop-blur-sm"
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          Loading...
        </motion.div>
      </div>
    </div>
  );
}
