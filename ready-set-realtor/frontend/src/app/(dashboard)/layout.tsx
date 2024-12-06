import { DashboardNav } from "@/components/dashboard/nav"
import { UserNav } from "@/components/dashboard/user-nav"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 hidden md:flex">
            <a className="mr-6 flex items-center space-x-2" href="/">
              <span className="hidden font-bold sm:inline-block">
                Ready Set Realtor
              </span>
            </a>
            <DashboardNav />
          </div>
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <div className="w-full flex-1 md:w-auto md:flex-none">
              {/* Add search functionality here */}
            </div>
            <UserNav />
          </div>
        </div>
      </header>
      <div className="container flex-1 space-y-4 p-8 pt-6">
        {children}
      </div>
    </div>
  )
} 