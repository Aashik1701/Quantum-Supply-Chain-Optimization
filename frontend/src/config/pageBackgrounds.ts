// Map routes to their background video URLs. Replace values per page as needed.
export const PAGE_BACKGROUND_VIDEOS: Record<string, string> = {
  '/': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
  '/dashboard': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
  '/optimization': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
  '/data': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
  '/results': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
  '/settings': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
  '/about': 'https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724',
}

export function getBackgroundForPath(pathname: string): string | undefined {
  // Exact match first
  if (PAGE_BACKGROUND_VIDEOS[pathname]) return PAGE_BACKGROUND_VIDEOS[pathname]
  // Try to match by first segment (e.g., /dashboard/123)
  const first = '/' + pathname.split('/').filter(Boolean)[0]
  if (PAGE_BACKGROUND_VIDEOS[first]) return PAGE_BACKGROUND_VIDEOS[first]
  // Fallback to home video
  return PAGE_BACKGROUND_VIDEOS['/']
}
