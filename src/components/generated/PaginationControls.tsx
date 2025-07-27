import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { motion } from 'framer-motion';
interface PaginationControlsProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange: (itemsPerPage: number) => void;
  mpid?: string;
}
const PaginationControls: React.FC<PaginationControlsProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  onItemsPerPageChange
}) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);
  const getVisiblePages = (): (number | string)[] => {
    const delta = 2;
    const range: number[] = [];
    const rangeWithDots: (number | string)[] = [];
    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }
    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }
    rangeWithDots.push(...range);
    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages);
    }
    return rangeWithDots;
  };
  const visiblePages = getVisiblePages();
  if (totalPages <= 1) {
    return <motion.div initial={{
      opacity: 0,
      y: 20
    }} animate={{
      opacity: 1,
      y: 0
    }} transition={{
      duration: 0.3
    }} className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl p-6 mt-8 shadow-sm" data-magicpath-id="0" data-magicpath-path="PaginationControls.tsx">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4" data-magicpath-id="1" data-magicpath-path="PaginationControls.tsx">
          <div className="flex items-center gap-4" data-magicpath-id="2" data-magicpath-path="PaginationControls.tsx">
            <label htmlFor="items-per-page" className="text-sm font-medium text-gray-700" data-magicpath-id="3" data-magicpath-path="PaginationControls.tsx">
              Show:
            </label>
            <select id="items-per-page" value={itemsPerPage} onChange={e => onItemsPerPageChange(Number(e.target.value))} className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900" data-magicpath-id="4" data-magicpath-path="PaginationControls.tsx">
              <option value={10} data-magicpath-id="5" data-magicpath-path="PaginationControls.tsx">10</option>
              <option value={25} data-magicpath-id="6" data-magicpath-path="PaginationControls.tsx">25</option>
              <option value={50} data-magicpath-id="7" data-magicpath-path="PaginationControls.tsx">50</option>
              <option value={100} data-magicpath-id="8" data-magicpath-path="PaginationControls.tsx">100</option>
            </select>
            <span className="text-sm text-gray-600" data-magicpath-id="9" data-magicpath-path="PaginationControls.tsx">per page</span>
          </div>
          <p className="text-sm text-gray-600" data-magicpath-id="10" data-magicpath-path="PaginationControls.tsx">
            Showing <strong data-magicpath-id="11" data-magicpath-path="PaginationControls.tsx">{startItem}</strong> to <strong data-magicpath-id="12" data-magicpath-path="PaginationControls.tsx">{endItem}</strong> of <strong data-magicpath-id="13" data-magicpath-path="PaginationControls.tsx">{totalItems}</strong> profiles
          </p>
        </div>
      </motion.div>;
  }
  return <motion.nav initial={{
    opacity: 0,
    y: 20
  }} animate={{
    opacity: 1,
    y: 0
  }} transition={{
    duration: 0.3
  }} className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl p-6 mt-8 shadow-sm" aria-label="Pagination navigation" data-magicpath-id="14" data-magicpath-path="PaginationControls.tsx">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6" data-magicpath-id="15" data-magicpath-path="PaginationControls.tsx">
        {/* Items per page and info */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-4" data-magicpath-id="16" data-magicpath-path="PaginationControls.tsx">
          <div className="flex items-center gap-4" data-magicpath-id="17" data-magicpath-path="PaginationControls.tsx">
            <label htmlFor="items-per-page" className="text-sm font-medium text-gray-700" data-magicpath-id="18" data-magicpath-path="PaginationControls.tsx">
              Show:
            </label>
            <select id="items-per-page" value={itemsPerPage} onChange={e => onItemsPerPageChange(Number(e.target.value))} className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50 backdrop-blur-sm text-gray-900" data-magicpath-id="19" data-magicpath-path="PaginationControls.tsx">
              <option value={10} data-magicpath-id="20" data-magicpath-path="PaginationControls.tsx">10</option>
              <option value={25} data-magicpath-id="21" data-magicpath-path="PaginationControls.tsx">25</option>
              <option value={50} data-magicpath-id="22" data-magicpath-path="PaginationControls.tsx">50</option>
              <option value={100} data-magicpath-id="23" data-magicpath-path="PaginationControls.tsx">100</option>
            </select>
            <span className="text-sm text-gray-600" data-magicpath-id="24" data-magicpath-path="PaginationControls.tsx">per page</span>
          </div>
          <p className="text-sm text-gray-600" data-magicpath-id="25" data-magicpath-path="PaginationControls.tsx">
            Showing <strong data-magicpath-id="26" data-magicpath-path="PaginationControls.tsx">{startItem}</strong> to <strong data-magicpath-id="27" data-magicpath-path="PaginationControls.tsx">{endItem}</strong> of <strong data-magicpath-id="28" data-magicpath-path="PaginationControls.tsx">{totalItems}</strong> profiles
          </p>
        </div>

        {/* Pagination controls */}
        <div className="flex items-center gap-2" data-magicpath-id="29" data-magicpath-path="PaginationControls.tsx">
          {/* First page */}
          <button onClick={() => onPageChange(1)} disabled={currentPage === 1} className="p-2 rounded-lg border border-gray-200 bg-white/50 backdrop-blur-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200" aria-label="Go to first page" data-magicpath-id="30" data-magicpath-path="PaginationControls.tsx">
            <ChevronsLeft className="w-4 h-4" data-magicpath-id="31" data-magicpath-path="PaginationControls.tsx" />
          </button>

          {/* Previous page */}
          <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1} className="p-2 rounded-lg border border-gray-200 bg-white/50 backdrop-blur-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200" aria-label="Go to previous page" data-magicpath-id="32" data-magicpath-path="PaginationControls.tsx">
            <ChevronLeft className="w-4 h-4" data-magicpath-id="33" data-magicpath-path="PaginationControls.tsx" />
          </button>

          {/* Page numbers */}
          <div className="flex items-center gap-1" data-magicpath-id="34" data-magicpath-path="PaginationControls.tsx">
            {visiblePages.map((page, index) => {
            if (page === '...') {
              return <span key={`dots-${index}`} className="px-3 py-2 text-gray-500" data-magicpath-uuid={(page as any)["mpid"] ?? "unsafe"} data-magicpath-id="35" data-magicpath-path="PaginationControls.tsx">
                    ...
                  </span>;
            }
            const pageNumber = page as number;
            const isCurrentPage = pageNumber === currentPage;
            return <motion.button key={pageNumber} onClick={() => onPageChange(pageNumber)} className={`px-3 py-2 rounded-lg border transition-all duration-200 ${isCurrentPage ? 'bg-blue-600 text-white border-blue-600 shadow-sm' : 'border-gray-200 bg-white/50 backdrop-blur-sm hover:bg-gray-50 text-gray-700'}`} whileHover={{
              scale: 1.05
            }} whileTap={{
              scale: 0.95
            }} aria-label={`Go to page ${pageNumber}`} aria-current={isCurrentPage ? 'page' : undefined} data-magicpath-uuid={(page as any)["mpid"] ?? "unsafe"} data-magicpath-id="36" data-magicpath-path="PaginationControls.tsx">
                  {pageNumber}
                </motion.button>;
          })}
          </div>

          {/* Next page */}
          <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages} className="p-2 rounded-lg border border-gray-200 bg-white/50 backdrop-blur-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200" aria-label="Go to next page" data-magicpath-id="37" data-magicpath-path="PaginationControls.tsx">
            <ChevronRight className="w-4 h-4" data-magicpath-id="38" data-magicpath-path="PaginationControls.tsx" />
          </button>

          {/* Last page */}
          <button onClick={() => onPageChange(totalPages)} disabled={currentPage === totalPages} className="p-2 rounded-lg border border-gray-200 bg-white/50 backdrop-blur-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200" aria-label="Go to last page" data-magicpath-id="39" data-magicpath-path="PaginationControls.tsx">
            <ChevronsRight className="w-4 h-4" data-magicpath-id="40" data-magicpath-path="PaginationControls.tsx" />
          </button>
        </div>
      </div>
    </motion.nav>;
};
export default PaginationControls;