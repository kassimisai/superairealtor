import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const items = [
  {
    title: "Dashboard",
    href: "/dashboard",
  },
  {
    title: "Leads",
    href: "/dashboard/leads",
  },
  {
    title: "Communications",
    href: "/dashboard/communications",
  },
  {
    title: "Documents",
    href: "/dashboard/documents",
  },
  {
    title: "Settings",
    href: "/dashboard/settings",
  },
]

export function DashboardNav() {
  const pathname = usePathname()

  return (
    <nav className="flex items-center space-x-6 text-sm font-medium">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            "transition-colors hover:text-foreground/80",
            pathname === item.href ? "text-foreground" : "text-foreground/60"
          )}
        >
          {item.title}
        </Link>
      ))}
    </nav>
  )
} 