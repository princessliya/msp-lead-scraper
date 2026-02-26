import { cn } from '../../lib/cn'

export default function Spinner({ className }: { className?: string }) {
  return (
    <div className={cn('animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full', className)} />
  )
}
