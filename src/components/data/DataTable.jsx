import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUpDown, ArrowUp, ArrowDown, Loader2 } from 'lucide-react';

export default function DataTable({
  columns = [],
  data = [],
  loading = false,
  emptyState = {
    icon: null,
    title: 'No data available',
    description: 'There are no records to display.'
  },
  onRowClick,
  className = ''
}) {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data;
    
    return [...data].sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [data, sortConfig]);

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    } else if (sortConfig.key === key && sortConfig.direction === 'desc') {
      return setSortConfig({ key: null, direction: 'asc' });
    }
    setSortConfig({ key, direction });
  };

  const getAriaSort = (key) => {
    if (sortConfig.key !== key) return 'none'
    return sortConfig.direction === 'asc' ? 'ascending' : 'descending'
  }

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return <ArrowUpDown className="w-3.5 h-3.5 ml-1.5 opacity-50" />;
    return sortConfig.direction === 'asc'
      ? <ArrowUp className="w-3.5 h-3.5 ml-1.5 text-foreground" />
      : <ArrowDown className="w-3.5 h-3.5 ml-1.5 text-foreground" />;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-muted-foreground animate-spin mb-4" />
        <p className="text-muted-foreground">Loading data...</p>
      </div>
    );
  }

  if (!loading && data.length === 0) {
    const Icon = emptyState.icon;
    return (
      <div className="text-center py-12">
        {Icon && (
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-muted text-muted-foreground mb-3">
            <Icon className="h-6 w-6" />
          </div>
        )}
        <h3 className="mt-2 text-sm font-medium text-foreground">
          {emptyState.title}
        </h3>
        <p className="mt-1 text-sm text-muted-foreground">
          {emptyState.description}
        </p>
      </div>
    );
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <div className="inline-block min-w-full align-middle">
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-muted/30">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    scope="col"
                    aria-sort={column.sortable ? getAriaSort(column.key) : undefined}
                    className={
                      `px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider ${
                        column.sortable ? '' : ''
                      }`
                    }
                  >
                    {column.sortable ? (
                      <button
                        type="button"
                        onClick={() => requestSort(column.key)}
                        className="inline-flex items-center hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
                      >
                        {column.header}
                        {getSortIcon(column.key)}
                      </button>
                    ) : (
                      <div className="flex items-center">{column.header}</div>
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              <AnimatePresence>
                {sortedData.map((row, rowIndex) => (
                  <motion.tr
                    key={row.id || rowIndex}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className={`${
                      onRowClick ? 'hover:bg-muted/40 cursor-pointer' : ''
                    }`}
                    onClick={() => onRowClick && onRowClick(row)}
                  >
                    {columns.map((column) => (
                      <td
                        key={`${row.id || rowIndex}-${column.key}`}
                        className="px-6 py-4 whitespace-nowrap text-sm text-foreground"
                      >
                        {column.render ? column.render(row[column.key], row) : row[column.key]}
                      </td>
                    ))}
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
