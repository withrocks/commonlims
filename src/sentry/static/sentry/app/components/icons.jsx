import React from 'react';
import theme from 'app/utils/theme';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {
  faVial,
  faClipboardList,
  faUserCog,
  faStar,
  faFolder,
  faFolderOpen,
  faHistory,
  faChartBar,
  faCog,
  faExclamationCircle,
  faQuestionCircle,
  faChevronCircleRight,
  faChevronCircleLeft,
  faExclamationTriangle,
  faInfoCircle,
  faBug,
  faCaretUp,
  faCaretDown,
  faCaretRight,
  faCaretLeft,
} from '@fortawesome/free-solid-svg-icons';

// Find more fontawesome icons here: https://fontawesome.com/icons?d=gallery&s=solid&m=free

export const Substance = () => <FontAwesomeIcon icon={faVial} />;
export const Projects = () => <FontAwesomeIcon icon={faClipboardList} />;
export const AssignedToMe = () => <FontAwesomeIcon icon={faUserCog} />;
export const Bookmarks = () => <FontAwesomeIcon icon={faStar} />;
export const AvailableWork = () => <FontAwesomeIcon icon={faFolder} />;
export const WorkInProgress = () => <FontAwesomeIcon icon={faFolderOpen} />;
export const RecentlyViewed = () => <FontAwesomeIcon icon={faHistory} />;
export const Stats = () => <FontAwesomeIcon icon={faChartBar} />;
export const Settings = () => <FontAwesomeIcon icon={faCog} />;
export const Activity = () => <FontAwesomeIcon icon={faExclamationCircle} />;
export const Help = () => <FontAwesomeIcon icon={faQuestionCircle} />;
export const CollapseLeftSidebar = () => <FontAwesomeIcon icon={faChevronCircleLeft} />;
export const ExpandLeftSidebar = () => <FontAwesomeIcon icon={faChevronCircleRight} />;
export const Error = () => <FontAwesomeIcon icon={faExclamationCircle} />;
export const Warning = () => <FontAwesomeIcon icon={faExclamationTriangle} />;
export const Info = () => <FontAwesomeIcon icon={faInfoCircle} />;
export const Debug = () => <FontAwesomeIcon icon={faBug} />;
export const CaretUp = () => <FontAwesomeIcon icon={faCaretUp} />;
export const CaretDown = () => <FontAwesomeIcon icon={faCaretDown} />;
export const CaretRight = () => <FontAwesomeIcon icon={faCaretRight} />;
export const CaretLeft = () => <FontAwesomeIcon icon={faCaretLeft} />;

// Returns a colored icon for a particular issue
export function getIssueIcon(type, hasDefaultColor) {
  let icon;
  let color = null;

  if (type === 'error') {
    icon = Error;
    color = theme.alert.error.iconColor;
  } else if (type === 'warning') {
    icon = Warning;
    color = theme.alert.warning.iconColor;
  } else if (type === 'info') {
    icon = Info;
    color = theme.alert.info.iconColor;
  } else if (type === 'debug') {
    icon = Debug;
    color = theme.alert.info.iconColor;
  } else {
    throw Error('Unsupported issue type: ' + type);
  }
  const style = hasDefaultColor ? {color} : null;

  return <p style={style}>{icon()}</p>;
}
