import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const data = [
  {
    name: "Jan",
    total: 12,
  },
  {
    name: "Feb",
    total: 18,
  },
  {
    name: "Mar",
    total: 24,
  },
  {
    name: "Apr",
    total: 32,
  },
  {
    name: "May",
    total: 28,
  },
  {
    name: "Jun",
    total: 35,
  },
  {
    name: "Jul",
    total: 42,
  },
  {
    name: "Aug",
    total: 38,
  },
  {
    name: "Sep",
    total: 45,
  },
  {
    name: "Oct",
    total: 52,
  },
  {
    name: "Nov",
    total: 48,
  },
  {
    name: "Dec",
    total: 55,
  },
]

export function Overview() {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <XAxis
          dataKey="name"
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value: number) => `${value}`}
        />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="total"
          stroke="#8884d8"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
} 