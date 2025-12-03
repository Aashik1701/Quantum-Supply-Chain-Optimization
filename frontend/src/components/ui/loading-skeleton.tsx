import React from 'react'
import { cn } from '@/lib/utils'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-slate-700/50', className)}
      {...props}
    />
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-slate-800 rounded-lg shadow-md p-6 border border-slate-700">
      <Skeleton className="h-6 w-1/3 mb-4" />
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-5/6 mb-2" />
      <Skeleton className="h-4 w-4/6" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="bg-slate-800 rounded-lg shadow-md p-6 border border-slate-700">
      <Skeleton className="h-6 w-1/4 mb-6" />
      <div className="space-y-3">
        <Skeleton className="h-48 w-full" />
        <div className="flex gap-2 justify-center">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-3 w-20" />
        </div>
      </div>
    </div>
  )
}
