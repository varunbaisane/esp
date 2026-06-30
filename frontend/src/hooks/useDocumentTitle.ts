import { useEffect } from "react";

const APP_NAME = "Engineering Support Platform";

/**
 * Sets the browser tab title for the current page.
 *
 * Usage:
 *   useDocumentTitle("Dashboard")
 *   → "Dashboard • Engineering Support Platform"
 *
 *   useDocumentTitle("")
 *   → "Engineering Support Platform"
 */
export const useDocumentTitle = (pageTitle: string): void => {
  useEffect(() => {
    document.title = pageTitle ? `${pageTitle} • ${APP_NAME}` : APP_NAME;
  }, [pageTitle]);
};
