/**
 * This file is part of Madas.
 *
 * Madas is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Madas is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Madas.  If not, see <http://www.gnu.org/licenses/>.
 */


/**
 * madasChangeMainContent 
 * acts as a shallow controller between string function names and initialization/display of pages
 * it should only be called directly when processing the return from an ajax request
 * any time you wish to change the display based on a user action you should call 
 * to Ext.madasAuthorize() instead, as that will check authorization first, which can prevent odd
 * situations where a page displays but the content fails
 */
Ext.madasChangeMainContent = function(contentName, paramArray){
    
    //Ext.get('center').dom.innerHTML = '';
    var showMenu = true;
    var affectMenu = true;
    var cancelBackTarget = true; //whether or not this action should be invoked if a user clicks Cancel (where the variable is obeyed)
    
    Ext.QuickTips.init();
    
    switch (contentName) {
            
        case "dashboard": 
            if (paramArray) {
                resultContent = paramArray[0];
                params = paramArray[1];
                Ext.madasAuthorize(resultContent, params);
                break;
            }
            //default
            Ext.getCmp('center-panel').layout.setActiveItem('dashboard-panel'); 
            break;
            
        case "login":
            showMenu = false;
            cancelBackTarget = false;
            Ext.madasLoginInit(paramArray);
            Ext.getCmp('center-panel').layout.setActiveItem('login-container-panel');
            break;
            
        case "login:forgotpassword":
            showMenu = false;
            cancelBackTarget = false;
            Ext.madasForgotPasswordInit();
            Ext.getCmp('center-panel').layout.setActiveItem('forgot-password-container-panel');
            break;
            
        case "login:resetpassword":
            showMenu = false;
            cancelBackTarget = false;
            Ext.madasResetPasswordInit();
            Ext.getCmp('center-panel').layout.setActiveItem('resetpassword-container-panel');
            break;
            
        case "login:processLogout":
            cancelBackTarget = false;
            Ext.madasLogoutInit();
            break;
            
        case "admin:adminrequests":
            Ext.madasAdminRequestsInit();
            Ext.getCmp('center-panel').layout.setActiveItem('adminrequests-panel');
            break;
            
        case "admin:usersearch":
            Ext.madasUserSearchInit();
            Ext.getCmp('center-panel').layout.setActiveItem('usersearch-panel');
            break;
            
        case "admin:rejectedUsersearch":
            Ext.madasRejectedUserSearchInit();
            Ext.getCmp('center-panel').layout.setActiveItem('rejectedusersearch-panel');
            break;
            
        case "admin:deletedUsersearch":
            Ext.madasDeletedUserSearchInit();
            Ext.getCmp('center-panel').layout.setActiveItem('deletedusersearch-panel');
            break;
            
        case "admin:nodelist":
            Ext.madasNodeManagementInit();
            Ext.getCmp('center-panel').layout.setActiveItem('nodeManagementCmp');
            break;
            
        case "admin:useredit":
            cancelBackTarget = false;
            Ext.madasAdminUserEditInit(paramArray);
            Ext.getCmp('center-panel').layout.setActiveItem('adminuseredit-container-panel');
            break;
            
        case "user:myaccount":
            cancelBackTarget = false;
            Ext.madasUserEditInit(paramArray);
            Ext.getCmp('center-panel').layout.setActiveItem('useredit-container-panel');
            break;
            
        case "notauthorized":
            cancelBackTarget = false;
            Ext.getCmp('center-panel').layout.setActiveItem('notauthorized-panel');
            break;
            
        case "message":
            cancelBackTarget = false;
            affectMenu = false;
            Ext.madasMessage(paramArray);
            break;
            
        case 'experiment:my':
            experimentListStore.reload();
            Ext.getCmp('center-panel').layout.setActiveItem('experiment-list');
            break;
        case 'experiment:new':
            Ext.madasLoadExperiment(0);
        case 'experiment:view':
            Ext.getCmp('center-panel').layout.setActiveItem('experimentTitle');
            Ext.getCmp('expNav').getSelectionModel().selectFirstRow();            
            break;
            
        default:
            cancelBackTarget = false;
    }
    
    //always affect menu if we are initing the app
    if (contentName == Ext.madasInitFunction) {
        affectMenu = true;
    }
    
    //    if (affectMenu) {
    //        if (showMenu) {
    //            Ext.madasMenuShow();
    //        } else {
    //            Ext.madasMenuHide();
    //        }
    //    }
    
    Ext.madasMenuEnsure();
    
    if (cancelBackTarget) {
        Ext.madasCancelBackTarget = contentName;
    }
    
    //append the application path onto the URL as a means of making things bookmarkable
    //var regex = /\#.*$/;
    //window.location = window.location.replace(regex, "#" + contentName);
    
};

Ext.madasMessage = function(paramArray) {
    
    Ext.Msg.alert("", paramArray['message']);
    
}

/**
 * madasAjaxMetadataProcess
 * look at the other headers in the header of an ajax request for a livegrid or other Object
 * assessing whether the user has timed-out or is not authorized to perform that action
 */
Ext.madasAjaxMetadataProcess = function(ajaxData) {
    
    //look for specific sentinel values in the json
    //var authenticated = ajaxData.response.value.authenticated;
    //var authorized = ajaxData.response.value.authorized;
    
    var authenticated = ajaxData.authenticated;
    var authorized = ajaxData.authorized;
    
    if (authenticated != 1) {
        //trigger the login page
        Ext.madasIsLoggedIn = false;
        Ext.madasIsAdmin = false;
        Ext.getCmp('userMenu').setText('User: none');
        
        Ext.madasChangeMainContent('login');
        //return false to tell the JsonReader to abort
        return false;
    }
    
    if (authorized != 1) {
        //trigger a notauthorized page
        Ext.madasChangeMainContent('notauthorized');
        //return false to tell the JsonReader to abort
        return false;
    }
    
    return true;
    
}
