import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { formatDate, getInitials } from "@/lib/utils"

const recentLeads = [
  {
    id: "1",
    name: "John Smith",
    email: "john.smith@example.com",
    status: "New",
    date: "2024-01-05T10:00:00Z",
  },
  {
    id: "2",
    name: "Sarah Johnson",
    email: "sarah.j@example.com",
    status: "Contacted",
    date: "2024-01-04T15:30:00Z",
  },
  {
    id: "3",
    name: "Michael Brown",
    email: "michael.b@example.com",
    status: "Qualified",
    date: "2024-01-04T09:15:00Z",
  },
  {
    id: "4",
    name: "Emily Davis",
    email: "emily.d@example.com",
    status: "New",
    date: "2024-01-03T16:45:00Z",
  },
  {
    id: "5",
    name: "David Wilson",
    email: "david.w@example.com",
    status: "Contacted",
    date: "2024-01-03T11:20:00Z",
  },
]

export function RecentLeads() {
  return (
    <div className="space-y-8">
      {recentLeads.map((lead) => (
        <div key={lead.id} className="flex items-center">
          <Avatar className="h-9 w-9">
            <AvatarFallback>{getInitials(lead.name)}</AvatarFallback>
          </Avatar>
          <div className="ml-4 space-y-1">
            <p className="text-sm font-medium leading-none">{lead.name}</p>
            <p className="text-sm text-muted-foreground">{lead.email}</p>
          </div>
          <div className="ml-auto text-sm">
            <div className="flex items-center gap-2">
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  lead.status === "New"
                    ? "bg-blue-100 text-blue-800"
                    : lead.status === "Contacted"
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-green-100 text-green-800"
                }`}
              >
                {lead.status}
              </span>
              <span className="text-muted-foreground">
                {formatDate(lead.date)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
} 