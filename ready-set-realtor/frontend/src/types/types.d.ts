declare module 'tailwind-merge' {
  export function twMerge(...classLists: (string | undefined | null | false)[]): string;
}

declare module 'tailwindcss-animate' {
  const plugin: any;
  export default plugin;
}

declare module '@/components/ui/toaster' {
  export const Toaster: React.FC;
}

declare module '@/components/ui/button' {
  export const Button: React.FC<{
    variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
    size?: 'default' | 'sm' | 'lg';
    className?: string;
    children: React.ReactNode;
    [key: string]: any;
  }>;
}

declare module '@/components/ui/avatar' {
  export const Avatar: React.FC<{
    className?: string;
    children: React.ReactNode;
  }>;
  export const AvatarFallback: React.FC<{
    children: React.ReactNode;
  }>;
}

declare module '@/components/ui/dropdown-menu' {
  export const DropdownMenu: React.FC<{
    children: React.ReactNode;
  }>;
  export const DropdownMenuTrigger: React.FC<{
    asChild?: boolean;
    children: React.ReactNode;
  }>;
  export const DropdownMenuContent: React.FC<{
    className?: string;
    align?: 'start' | 'end' | 'center';
    forceMount?: boolean;
    children: React.ReactNode;
  }>;
  export const DropdownMenuItem: React.FC<{
    onSelect?: () => void;
    children: React.ReactNode;
  }>;
  export const DropdownMenuLabel: React.FC<{
    className?: string;
    children: React.ReactNode;
  }>;
  export const DropdownMenuSeparator: React.FC;
} 