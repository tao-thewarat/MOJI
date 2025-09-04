// /** @odoo-module **/

// import {registry} from "@web/core/registry";
// import {session} from "@web/session";
// import {browser} from "@web/core/browser/browser";
// import {deserializeDateTime, serializeDate, formatDate} from "@web/core/l10n/dates";
// import {useService} from "@web/core/utils/hooks";
// import {_t} from "@web/core/l10n/translation";
// import {ExpirationPanel} from "./expiration_panel";
// import {cookie} from "@web/core/browser/cookie";
// import {rpc} from "@web/core/network/rpc";

// const {DateTime} = luxon;
// import {Component, xml, useState} from "@odoo/owl";

// function daysUntil(datetime) {
//     const duration = datetime.diff(DateTime.utc(), "days");
//     return Math.round(duration.values.days);
// }

// export class SubscriptionManager {
//     constructor(env, {orm, notification}) {
//         this.env = env;
//         this.orm = orm;
//         this.notification = notification;
//         if (session.expiration_date) {
//             this.expirationDate = deserializeDateTime(session.expiration_date);
//         } else {
//             // If no date found, assume 1 month and hope for the best
//             this.expirationDate = DateTime.utc().plus({days: 30});
//         }
//         this.expirationReason = session.expiration_reason;
//         this.hasInstalledApps = "storeData" in session;
//         // "user" or "admin"
//         this.warningType = session.warning;
//         this.lastRequestStatus = null;
//         this.isWarningHidden = cookie.get("oe_instance_hide_panel");
//     }

//     get formattedExpirationDate() {
//         return formatDate(this.expirationDate, {format: "DDD"});
//     }

//     get daysLeft() {
//         return daysUntil(this.expirationDate);
//     }

//     get unregistered() {
//         return ["trial", "demo", false].includes(this.expirationReason);
//     }

//     hideWarning() {
//         // Hide warning for 24 hours.
//         cookie.set("oe_instance_hide_panel", true, 24 * 60 * 60);
//         this.isWarningHidden = true;
//     }

//     async buy() {
//         const limitDate = serializeDate(DateTime.utc().minus({days: 15}));
//         const args = [
//             [
//                 ["share", "=", false],
//                 ["login_date", ">=", limitDate],
//             ],
//         ];
//         const nbUsers = await this.orm.call("res.users", "search_count", args);
//         browser.location = `https://www.odoo.com/odoo-enterprise/upgrade?num_users=${nbUsers}`;
//     }

//     async submitCode(enterpriseCode) {
//         const [oldDate,] = await Promise.all([
//             this.orm.call("ir.config_parameter", "get_param", ["database.expiration_date"]),
//             this.orm.call("ir.config_parameter", "set_param", [
//                 "database.enterprise_code",
//                 enterpriseCode,
//             ])
//         ]);

//         await this.orm.call("publisher_warranty.contract", "update_notification", [[]]);

//         const [linkedSubscriptionUrl, linkedEmail, expirationDate] = await Promise.all([
//             this.orm.call("ir.config_parameter", "get_param", [
//                 "database.already_linked_subscription_url",
//             ]),
//             this.orm.call("ir.config_parameter", "get_param", ["database.already_linked_email"]),
//             this.orm.call("ir.config_parameter", "get_param", [
//                 "database.expiration_date",
//             ])
//         ]);

//         if (linkedSubscriptionUrl) {
//             this.lastRequestStatus = "link";
//             this.linkedSubscriptionUrl = linkedSubscriptionUrl;
//             this.mailDeliveryStatus = null;
//             this.linkedEmail = linkedEmail;
//         } else if (expirationDate !== oldDate) {
//             this.lastRequestStatus = "success";
//             this.expirationDate = deserializeDateTime(expirationDate);
//             if (this.daysLeft > 30) {
//                 this.notification.add(
//                     _t(
//                         "Thank you, your registration was successful! Your database is valid until %s.",
//                         this.formattedExpirationDate
//                     ),
//                     {type: "success"}
//                 );
//             }
//         } else {
//             this.lastRequestStatus = "error";
//         }
//     }

//     async checkStatus() {
//         await this.orm.call("publisher_warranty.contract", "update_notification", [[]]);

//         const expirationDateStr = await this.orm.call("ir.config_parameter", "get_param", [
//             "database.expiration_date",
//         ]);
//         this.lastRequestStatus = "update";
//         this.expirationDate = deserializeDateTime(expirationDateStr);
//     }

//     async sendUnlinkEmail() {
//         const sendUnlinkInstructionsUrl = await this.orm.call("ir.config_parameter", "get_param", [
//             "database.already_linked_send_mail_url",
//         ]);
//         this.mailDeliveryStatus = "ongoing";
//         const {result, reason} = await rpc(sendUnlinkInstructionsUrl);
//         if (result) {
//             this.mailDeliveryStatus = "success";
//         } else {
//             this.mailDeliveryStatus = "fail";
//             this.mailDeliveryStatusError = reason;
//         }
//     }

//     async renew() {
//         const enterpriseCode = await this.orm.call("ir.config_parameter", "get_param", [
//             "database.enterprise_code",
//         ]);

//         const url = "https://www.odoo.com/odoo-enterprise/renew";
//         const contractQueryString = enterpriseCode ? `?contract=${enterpriseCode}` : "";
//         browser.location = `${url}${contractQueryString}`;
//     }

//     async upsell() {
//         const limitDate = serializeDate(DateTime.utc().minus({days: 15}));
//         const [enterpriseCode, nbUsers] = await Promise.all([
//             this.orm.call("ir.config_parameter", "get_param", ["database.enterprise_code"]),
//             this.orm.call("res.users", "search_count", [
//                 [
//                     ["share", "=", false],
//                     ["login_date", ">=", limitDate],
//                 ],
//             ]),
//         ]);
//         const url = "https://www.odoo.com/odoo-enterprise/upsell";
//         const contractQueryString = enterpriseCode ? `&contract=${enterpriseCode}` : "";
//         browser.location = `${url}?num_users=${nbUsers}${contractQueryString}`;
//     }
// }

// class ExpiredSubscriptionBlockUI extends Component {
//     static props = {};
//     // TODO the "o_blockUI" div in there seems useless (it has 0 height and thus displays and does nothing)
//     static template = xml``;
//     static components = {ExpirationPanel};

//     setup() {
//         this.subscription = useState(useService("enterprise_subscription"));
//     }
// }

// export const enterpriseSubscriptionService = {
//     name: "enterprise_subscription",
//     dependencies: ["orm", "notification"],
//     start(env, {orm, notification}) {
//         registry
//             .category("main_components")
//             .add("expired_subscription_block_ui", {Component: ExpiredSubscriptionBlockUI});
//         return new SubscriptionManager(env, {orm, notification});
//     },
// };

// registry.category("services").add("enterprise_subscription", enterpriseSubscriptionService);
